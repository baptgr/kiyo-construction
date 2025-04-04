import os
import json
import asyncio
from typing import AsyncIterator, Dict, Any, Optional, List
import logging

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

You can also interact with Google Sheets to help with data management:
- Reading data from spreadsheets (use read_google_sheet tool)
- Writing data to spreadsheets (use write_google_sheet tool)

When working with spreadsheets:
1. Use A1 notation for ranges (e.g., 'Sheet1!A1:D10')
2. Properly format data for writing (2D array of values)
3. For sheet names with spaces or special characters, use single quotes around the sheet name
   Example: 'Bid Comparison'!A1:D10 (not Bid Comparison!A1:D10)
4. Make sure the sheet name exists in the spreadsheet - the default is usually "Bid Comparison"
5. Values must be a 2D array (array of arrays) where each inner array represents a row
   Example: [["Item", "Price"], ["Concrete", "85.00"]]

Be helpful, concise, and accurate in your responses. If you don't know something,
be honest about it instead of making up information.
"""

logger = logging.getLogger(__name__)

class ConstructionAgent(AgentInterface):
    """Implementation of the construction agent using OpenAI Agents SDK."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o", google_access_token: Optional[str] = None):
        """Initialize the construction agent.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            model_name: Model to use (default: gpt-4o)
            google_access_token: Google OAuth access token for sheets access
        """
        # Use provided API key or fall back to environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY or pass api_key parameter.")
        
        # Store Google access token
        self.google_access_token = google_access_token
        
        # Import tools from google_sheets_tools
        from .google_sheets_tools import (
            FunctionTool, read_sheet_tool, write_sheet_tool, 
            READ_SHEET_SCHEMA, WRITE_SHEET_SCHEMA
        )
        
        # Create our own tool instances with pre-configured access token
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
            tools=configured_tools
        )
        
        # Conversation memory (simple for demo)
        self.conversations = {}
        
    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        # Create a context object for the RunContextWrapper to access
        context = {}
        if self.google_access_token:
            # Store token in multiple places for different access patterns
            context["google_access_token"] = self.google_access_token
            context["tool_context"] = {"google_access_token": self.google_access_token}
            context["kwargs"] = {"google_access_token": self.google_access_token}
        
        # Use the run method from the example with context
        result = await Runner.run(
            self.agent, 
            message,
            context=context
        )
        
        # Format the response
        response = {
            "text": result.final_output,
            "conversation_id": conversation_id or "default"
        }
        
        return response
    
    async def process_message_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Process a message and yield chunks of the response as they're generated."""
        # Create a context object for the RunContextWrapper to access
        context = {}
        if self.google_access_token:
            # Store token in multiple places for different access patterns
            context["google_access_token"] = self.google_access_token
            context["tool_context"] = {"google_access_token": self.google_access_token}
            context["kwargs"] = {"google_access_token": self.google_access_token}
        
        # Use the streaming method with context
        result = Runner.run_streamed(
            self.agent, 
            input=message,
            context=context
        )
        
        try:
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
        except Exception as e:
            # Handle context errors gracefully
            if "ContextVar" in str(e) or "current_trace" in str(e):
                # Just yield a final chunk if we encounter trace errors
                yield {
                    "text": "",
                    "finished": True,
                    "conversation_id": conversation_id or "default"
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
            full_text = ""
            current_context = None
            streamed_result = None
            
            try:
                # Store the current context to use consistently
                import contextvars
                current_context = contextvars.copy_context()
                
                # Create a context object for the RunContextWrapper to access
                context = {}
                if self.google_access_token:
                    # Store token in multiple places for different access patterns
                    context["google_access_token"] = self.google_access_token
                    context["tool_context"] = {"google_access_token": self.google_access_token}
                    context["kwargs"] = {"google_access_token": self.google_access_token}
                
                # Get the streamed result inside the same context with context object
                streamed_result = Runner.run_streamed(
                    self.agent, 
                    input=message,
                    context=context
                )
                
                # Process the stream within the same context
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
                                "conversation_id": conversation_id or "default"
                            }
                            
                    # When we reach the final output, signal completion
                    elif event.type == "final_output_event":
                        # If there's a final output that's different, send it
                        final_output = getattr(event.data, "final_output", None)
                        if final_output and final_output != full_text:
                            yield {
                                "text": final_output,
                                "finished": False,
                                "conversation_id": conversation_id or "default"
                            }
                        
                        # Send a final empty chunk to indicate we're done
                        yield {
                            "text": "",
                            "finished": True,
                            "conversation_id": conversation_id or "default"
                        }
            except Exception as e:
                # For any errors, log them and signal completion
                error_msg = str(e)
                print(f"Error in token stream: {error_msg}")
                
                # Handle ContextVar errors gracefully
                if "ContextVar" in error_msg or "current_trace" in error_msg or "was created in a different Context" in error_msg:
                    print("Context variable error detected - suppressing to avoid affecting user experience")
                    # Complete the stream without error for context variable issues
                    yield {
                        "text": full_text if full_text else "",
                        "finished": True,
                        "conversation_id": conversation_id or "default"
                    }
                else:
                    # For other errors, pass them through
                    yield {
                        "error": str(e),
                        "finished": True,
                        "conversation_id": conversation_id or "default"
                    }
            finally:
                # Cleanup any resources if needed
                streamed_result = None
        
        # Return the token stream
        return token_stream()


class ConstructionAgentFactory:
    """Factory for creating construction agent instances."""
    
    def __init__(self, api_key: Optional[str] = None, google_access_token: Optional[str] = None):
        self.api_key = api_key
        self.google_access_token = google_access_token
        
    def create_agent(self, agent_type: str = "construction") -> AgentInterface:
        """Create and return an agent of the specified type."""
        if agent_type.lower() == "construction":
            return ConstructionAgent(
                api_key=self.api_key,
                google_access_token=self.google_access_token
            )
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}") 