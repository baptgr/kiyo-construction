import os
import json
import asyncio
from typing import AsyncIterator, Dict, Any, Optional, List

# Import from the installed package
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from .interfaces import AgentInterface

# Default instructions for the construction agent
CONSTRUCTION_AGENT_INSTRUCTIONS = """
You are an AI assistant for a construction company called Kiyo Construction. 
You specialize in helping with construction-related questions, such as:
- Materials and their properties
- Construction techniques and best practices
- Building codes and regulations
- Cost estimation
- Project planning and timelines

Be helpful, concise, and accurate in your responses. If you don't know something,
be honest about it instead of making up information.
"""


class ConstructionAgent(AgentInterface):
    """Implementation of the construction agent using OpenAI Agents SDK."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        """Initialize the construction agent.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model_name: Model to use (default: gpt-4o)
        """
        # Use provided API key or fall back to environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or pass api_key parameter.")
        
        # Create the agent - using the simple approach from GitHub examples
        self.agent = Agent(
            name="Construction Assistant",
            instructions=CONSTRUCTION_AGENT_INSTRUCTIONS,
        )
        
        # Conversation memory (simple for demo)
        self.conversations = {}
        
    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        # Use the run method from the example
        result = await Runner.run(self.agent, message)
        
        # Format the response
        response = {
            "text": result.final_output,
            "conversation_id": conversation_id or "default"
        }
        
        return response
    
    async def process_message_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Process a message and yield chunks of the response as they're generated."""
        # Use the streaming method from the GitHub example
        result = Runner.run_streamed(self.agent, input=message)
        
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                yield {
                    "text": event.data.delta,
                    "finished": False,
                    "conversation_id": conversation_id or "default"
                }
            elif event.type == "final_output_event":
                # Send a final event indicating completion
                yield {
                    "text": "",
                    "finished": True,
                    "conversation_id": conversation_id or "default"
                }


class ConstructionAgentFactory:
    """Factory for creating construction agent instances."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
    def create_agent(self, agent_type: str = "construction") -> AgentInterface:
        """Create and return an agent of the specified type."""
        if agent_type.lower() == "construction":
            return ConstructionAgent(api_key=self.api_key)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}") 