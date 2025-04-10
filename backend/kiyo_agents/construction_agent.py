import os
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated
import logging
import json

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from .google_sheets_service import GoogleSheetsService
from .tools import create_google_sheets_tools

logger = logging.getLogger(__name__)

# Global memory saver instance
_memory_saver = MemorySaver()

# Updated instructions for the construction agent
CONSTRUCTION_AGENT_INSTRUCTIONS = """
You are an AI assistant for bid leveling. You specialize in helping create bid levels for construction projects.

The bid leveling is done in a google sheet.

You can also interact with Google Sheets when asked, to help with data management:
- Getting sheet names (use get_sheet_names tool)
- Reading data from spreadsheets (use read_google_sheet tool)
- Writing data to spreadsheets (use write_google_sheet tool)

When working with spreadsheets:
1. Ensure you use the correct sheet name in the call (use get_sheet_names tool to get the sheet names)
2. Always read the content of a sheet right before writing to it and after each user message (use read_google_sheet tool) as the user may have edited the sheet
3. Use A1 notation for ranges (e.g., 'Sheet1!A1:D10')
4. Properly format data for writing (2D array of values)
5. Do not rewrite in the chat the data / tables you wrote in the sheet, just say that you wrote the data to the sheet

Be helpful, concise, and accurate in your responses. If you don't know something,
be honest about it instead of making up information.
"""

class AgentState(TypedDict):
    """Type definition for the agent's state"""
    messages: Annotated[List[BaseMessage], add_messages]
    google_access_token: Optional[str]
    spreadsheet_id: Optional[str]

class ConstructionAgent:
    """Implementation of the construction agent using LangGraph."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model_name: str = "gpt-4o",
                 google_access_token: Optional[str] = None,
                 spreadsheet_id: Optional[str] = None):
        """Initialize the construction agent."""
        self.api_key = api_key
        self.model_name = model_name
        self.google_access_token = google_access_token
        self.spreadsheet_id = spreadsheet_id  
        # Use the global memory saver
        self.memory = _memory_saver
        self.graph = self._create_graph()

        logger.info(f"Google access token: {self.google_access_token}")
        logger.info(f"Spreadsheet ID: {self.spreadsheet_id}")

    def _create_tools(self) -> List[Dict[str, Any]]:
        """Create the tools for the agent."""
        tools = []
        
        if self.google_access_token:
            sheets_service = GoogleSheetsService(self.google_access_token)
            tools.extend(create_google_sheets_tools(sheets_service, self.spreadsheet_id))
        
        return tools

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        # Initialize the graph with our state type
        workflow = StateGraph(AgentState)
        
        # Create the LLM
        llm = ChatOpenAI(
            model=self.model_name,
            temperature=0,
            openai_api_key=self.api_key,
            streaming=True
        )
        
        # Create tools
        tools = self._create_tools()
        
        # Bind tools to the LLM
        llm_with_tools = llm.bind_tools(tools)
        
        # Create the agent node
        def agent_node(state: AgentState) -> Dict:
            """Process messages and generate responses."""
            messages = state["messages"]
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Add nodes to the graph
        workflow.add_node("agent", agent_node)
        workflow.add_edge(START, "agent")
        
        if tools:
            # Create tool node with proper error handling
            tool_node = ToolNode(tools)

            # Add tool node to graph
            workflow.add_node("tools", tool_node)

            # Define conditional edges with better logic
            def should_continue(state: AgentState):
                #logger.info("Should continue switch")
                #logger.info(f"State: {state}")
                messages = state["messages"]
                last_message = messages[-1]
                if last_message.tool_calls:
                    return "tools"
                return END
                            

            workflow.add_conditional_edges(
                "agent",
                should_continue,
                ["tools", END]
            )
        else:
            workflow.add_edge("agent", END)

        workflow.add_edge("tools", "agent")
        
        # Compile the graph with memory support
        return workflow.compile(checkpointer=self.memory)

    def process_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        logger.info(f"Processing message for conversation {conversation_id}")
        
        # Get existing messages from memory if conversation_id exists
        existing_messages = []
        if conversation_id:
            try:
                # Try to get existing state from memory
                existing_state = self.memory.get_state(conversation_id)
                if existing_state and "messages" in existing_state:
                    existing_messages = existing_state["messages"]
                    logger.info(f"Found existing messages for conversation {conversation_id}")
            except Exception as e:
                logger.warning(f"Could not retrieve messages for conversation {conversation_id}: {e}")
        
        # Create initial state with existing messages + new message
        state = AgentState(
            messages=existing_messages + [HumanMessage(content=message)],
            google_access_token=self.google_access_token,
            spreadsheet_id=spreadsheet_id
        )
        
        # Add configuration for thread memory
        config = {"configurable": {"thread_id": conversation_id}} if conversation_id else {}
        
        # Run the graph with thread configuration
        result = self.graph.invoke(state, config=config)
        
        # Extract the final message
        final_message = result["messages"][-1]
        return {
            "text": final_message.content,
            "tool_calls": getattr(final_message, "tool_calls", None)
        }

    def process_message_stream(
        self, 
        message: str,
        conversation_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message and stream the response."""
        logger.info(f"Starting message stream processing for conversation {conversation_id}")
        
        # Get existing messages from memory if conversation_id exists
        existing_messages = []
        if conversation_id:
            try:
                # Try to get existing state from memory
                existing_state = self.memory.get_state(conversation_id)
                if existing_state and "messages" in existing_state:
                    existing_messages = existing_state["messages"]
                    logger.info(f"Found existing messages for conversation {conversation_id}")
            except Exception as e:
                logger.warning(f"Could not retrieve messages for conversation {conversation_id}: {e}")
        
        # Create initial state with existing messages + new message
        state = AgentState(
            messages=existing_messages + [HumanMessage(content=message)],
            google_access_token=self.google_access_token,
            spreadsheet_id=spreadsheet_id   
        )
        
        # Add configuration for thread memory
        config = {"configurable": {"thread_id": conversation_id}} if conversation_id else {}
        
        #logger.info("Starting graph streaming")
        # Stream the response with thread configuration
        accumulated_text = ""
        for stream_type, event in self.graph.stream(state, config=config, stream_mode=["messages", "updates"]):
            import pprint
            #logger.info(f"Received event: {pprint.pformat(event)}")
            if stream_type == "messages":
                message, metadata = event
                if hasattr(message, 'content'):
                    # Only update accumulated text if there's actual content
                    if message.content:
                        accumulated_text += message.content
                        chunk = {
                            "text": accumulated_text,
                            "tool_calls": getattr(message, "tool_calls", None),
                            "type": "message"
                        }
                        #logger.info(f"Yielding message chunk: {chunk}...")
                        yield chunk
            elif stream_type == "updates" and "tool_calls" in event:
                # Only yield tool calls if they have valid names
                tool_calls = event.get("tool_calls", [])
                if tool_calls and any(call.get("name") for call in tool_calls):
                    chunk = {
                        "tool_calls": tool_calls,
                        "type": "tool_call"
                    }
                    #logger.info(f"Yielding tool call chunk: {json.dumps(chunk['tool_calls'])}")
                    yield chunk
                
        logger.info("Message stream processing completed") 