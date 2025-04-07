import os
import json
import asyncio
from typing import AsyncIterator, Dict, Any, Optional, List
import logging
import pickle
from pathlib import Path
import uuid

# Import from the installed package
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from .interfaces import AgentInterface
from .google_sheets_tools import google_sheets_tools

# Updated instructions for the construction agent with Google Sheets capabilities
CONSTRUCTION_AGENT_INSTRUCTIONS = """
You are an AI assistant for a construction company called Kiyo Construction. 
You specialize in helping with construction-related questions, such as:
- Materials and their properties
- Construction techniques and best practices
- Building codes and regulations
- Cost estimation
- Project planning and timelines

You can also interact with Google Sheets when asked, to help with data management:
- Reading data from spreadsheets (use read_google_sheet tool)
- Writing data to spreadsheets (use write_google_sheet tool)

When working with spreadsheets:
1. Use A1 notation for ranges (e.g., 'Sheet1!A1:D10')
2. Properly format data for writing (2D array of values)

Be helpful, concise, and accurate in your responses. If you don't know something,
be honest about it instead of making up information.
"""

logger = logging.getLogger(__name__)

class ConstructionAgent(AgentInterface):
    """Implementation of the construction agent using OpenAI Agents SDK."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model_name: str = "gpt-4o", 
                 google_access_token: Optional[str] = None,
                 memory_store: Optional[Any] = None):
        """Initialize the construction agent."""
        
        # Store the API key
        self.api_key = api_key
        
        # Store Google access token if provided
        self.google_access_token = google_access_token
        
        # Store memory store
        self.memory = memory_store
        
        # Import tools from google_sheets_tools
        from .google_sheets_tools import (
            FunctionTool, read_sheet_tool, write_sheet_tool, 
            READ_SHEET_SCHEMA, WRITE_SHEET_SCHEMA
        )
        
        # Initialize empty list of tools
        configured_tools = []
        
        if self.google_access_token:
            # Create read sheet tool with pre-configured access token
            async def read_with_token(ctx, args):
                return await read_sheet_tool(ctx, args, token=self.google_access_token)
                
            # Create write sheet tool with pre-configured access token
            async def write_with_token(ctx, args):
                return await write_sheet_tool(ctx, args, token=self.google_access_token)
            
            # Create the tool instances with our wrapped functions
            read_sheet = FunctionTool(
                name="read_google_sheet",
                description="Read data from a Google Sheet. Requires spreadsheet ID and range in A1 notation.",
                params_json_schema=READ_SHEET_SCHEMA,
                on_invoke_tool=read_with_token
            )
            
            write_sheet = FunctionTool(
                name="write_google_sheet",
                description="Write data to a Google Sheet. Requires spreadsheet ID, range, and 2D array of values.",
                params_json_schema=WRITE_SHEET_SCHEMA,
                on_invoke_tool=write_with_token
            )
            
            configured_tools = [read_sheet, write_sheet]
        
        # Create the agent with our configured tools (or empty list if no token)
        self.agent = Agent(
            name="Construction Assistant",
            instructions=CONSTRUCTION_AGENT_INSTRUCTIONS,
            tools=configured_tools,
            model="gpt-4"  # Explicitly set the model name
        )
        
        # Store the model name for use in streaming
        self.model_name = model_name
    
    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        # Use default conversation_id if not provided
        conversation_id = conversation_id or str(uuid.uuid4())
        
        # Get conversation context if we have a memory store
        context = ""
        if self.memory:
            # Ensure conversation exists
            await self.memory.get_or_create_conversation(conversation_id)
            # Get context from previous messages
            context = await self.memory.get_conversation_context(conversation_id)
            # Store the user message
            await self.memory.add_message(conversation_id, "user", message)
        
        # Create a context object for the RunContextWrapper to access
        tool_context = {}
        if self.google_access_token:
            tool_context.update({
                "google_access_token": self.google_access_token,
                "tool_context": {"google_access_token": self.google_access_token},
                "kwargs": {"google_access_token": self.google_access_token}
            })
        
        # Enhance message with context if exists
        enhanced_message = f"{context}User: {message}" if context else message
        
        # Use the run method with context
        logger.info(f"Running agent with message")
        result = await Runner.run(
            self.agent, 
            enhanced_message,
            context=tool_context
        )
        
        # Store the assistant's response if we have a memory store
        if self.memory:
            await self.memory.add_message(
                conversation_id, 
                "assistant", 
                result.final_output,
                item_type="response",
                metadata={"items": [item.dict() for item in result.new_items]}
            )
        
        # Format the response
        response = {
            "text": result.final_output,
            "conversation_id": conversation_id
        }
        
        return response
    
    async def process_message_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Process a message and yield chunks of the response as they're generated."""
        # Use default conversation_id if not provided
        conversation_id = conversation_id or str(uuid.uuid4())
        
        # Get conversation context if we have a memory store
        context = ""
        if self.memory:
            # Ensure conversation exists
            await self.memory.get_or_create_conversation(conversation_id)
            # Get context from previous messages
            context = await self.memory.get_conversation_context(conversation_id)
            # Store the user message
            await self.memory.add_message(conversation_id, "user", message)
        
        # Create a context object for the RunContextWrapper to access
        tool_context = {}
        if self.google_access_token:
            tool_context.update({
                "google_access_token": self.google_access_token,
                "tool_context": {"google_access_token": self.google_access_token},
                "kwargs": {"google_access_token": self.google_access_token}
            })
        
        # Enhance message with context if exists
        enhanced_message = f"{context}User: {message}" if context else message
        
        # Use the streaming method with context
        result = Runner.run_streamed(
            self.agent, 
            input=enhanced_message,
            context=tool_context
        )
        
        # Variable to collect the full response
        full_response = ""
        
        try:
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    # Collect the response
                    full_response += event.data.delta
                    
                    yield {
                        "text": event.data.delta,
                        "finished": False,
                        "conversation_id": conversation_id
                    }
                elif event.type == "final_output_event":
                    # Store the complete response if we have a memory store
                    if self.memory and full_response:
                        await self.memory.add_message(
                            conversation_id, 
                            "assistant", 
                            full_response,
                            item_type="response",
                            metadata={"items": [item.dict() for item in result.new_items]}
                        )
                    
                    # Send a final event indicating completion
                    yield {
                        "text": "",
                        "finished": True,
                        "conversation_id": conversation_id
                    }
        except Exception as e:
            # Handle context errors gracefully
            if "ContextVar" in str(e) or "current_trace" in str(e):
                # Just yield a final chunk if we encounter trace errors
                yield {
                    "text": "",
                    "finished": True,
                    "conversation_id": conversation_id
                }
            else:
                # Re-raise other errors
                raise
    
    def get_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """
        Get a streaming response from the agent.
        
        This uses the raw streaming capability of the OpenAI Agents SDK to provide
        true real-time token-by-token streaming. Each token is yielded as soon as
        it's generated by the model.
        
        Args:
            message: The message to process
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            An async iterator yielding chunks of the response
        """
        # Create an async generator to handle the stream
        async def token_stream():
            # Use default conversation_id if not provided
            conv_id = conversation_id or str(uuid.uuid4())
            logger.info(f"get_stream called with conversation_id: {conv_id}")
            
            # Get conversation context if we have a memory store
            context = ""
            if self.memory:
                # Ensure conversation exists
                await self.memory.get_or_create_conversation(conv_id)
                # Get context from previous messages
                context = await self.memory.get_conversation_context(conv_id)
                # Store the user message
                await self.memory.add_message(conv_id, "user", message)
            
            # Enhance message with context if exists
            enhanced_message = f"{context}User: {message}" if context else message
            
            full_text = ""
            
            try:
                # Create a context object for the RunContextWrapper to access
                tool_context = {}
                
                if self.google_access_token:
                    tool_context.update({
                        "google_access_token": self.google_access_token,
                        "tool_context": {"google_access_token": self.google_access_token},
                        "kwargs": {"google_access_token": self.google_access_token}
                    })
                
                # Get the streamed result with context
                logger.info(f"Running streaming agent with message")
                streamed_result = Runner.run_streamed(
                    self.agent, 
                    input=enhanced_message,
                    context=tool_context
                )
                
                # Process the stream
                async for event in streamed_result.stream_events():
                    # For raw response events (actual tokens), yield them immediately
                    if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                        # Capture the new token
                        new_token = event.data.delta
                        
                        # Update our running text
                        if new_token:
                            full_text += new_token
                            
                            # Send the updated text
                            yield {
                                "text": full_text,
                                "finished": False,
                                "conversation_id": conv_id
                            }
                            
                    # When we reach the final output, signal completion
                    elif event.type == "final_output_event":
                        # Store the complete response if we have a memory store
                        if self.memory and full_text:
                            await self.memory.add_message(
                                conv_id, 
                                "assistant", 
                                full_text,
                                item_type="response",
                                metadata={"items": [item.dict() for item in streamed_result.new_items]}
                            )
                        
                        # Send a final event indicating completion
                        yield {
                            "text": "",
                            "finished": True,
                            "conversation_id": conv_id
                        }
            except Exception as e:
                # Log the error and yield an error response
                logger.error(f"Error in token_stream: {e}")
                
                yield {
                    "text": f"Error: {str(e)}",
                    "error": str(e),
                    "finished": True,
                    "conversation_id": conv_id
                }
            
        # Return the token stream generator
        return token_stream()


class ConstructionAgentFactory:
    """Factory for creating construction agent instances."""
    
    def __init__(self, api_key: Optional[str] = None, google_access_token: Optional[str] = None, memory_store: Optional[Any] = None):
        logger.info("Initializing ConstructionAgentFactory")
        self.api_key = api_key
        self.google_access_token = google_access_token
        self.memory_store = memory_store
        logger.info(f"Factory initialized with API key: {'set' if api_key else 'not set'}, " 
                   f"Google token: {'set' if google_access_token else 'not set'}, "
                   f"Memory store: {'set' if memory_store else 'not set'}")
        
    def create_agent(self, agent_type: str = "construction") -> AgentInterface:
        """Create and return an agent of the specified type."""
        logger.info(f"Factory creating agent of type: {agent_type}")
        if agent_type.lower() == "construction":
            agent = ConstructionAgent(
                api_key=self.api_key,
                google_access_token=self.google_access_token,
                memory_store=self.memory_store
            )
            logger.info(f"Factory created construction agent with ID: {id(agent)}")
            return agent
        else:
            logger.error(f"Unsupported agent type requested: {agent_type}")
            raise ValueError(f"Unsupported agent type: {agent_type}") 