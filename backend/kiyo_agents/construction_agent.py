import os
from typing import List, Dict, Any, AsyncIterator, Optional
from typing_extensions import TypedDict, Annotated
import logging
import json

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, Graph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain.tools import tool

from .google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)

# Updated instructions for the construction agent
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

class AgentState(TypedDict):
    """Type definition for the agent's state"""
    messages: Annotated[List[BaseMessage], add_messages]
    google_access_token: Optional[str]
    spreadsheet_id: Optional[str]

class ConstructionAgent:
    """Implementation of the construction agent using LangGraph."""
    
    def __init__(self, api_key: Optional[str] = None, 
                 model_name: str = "gpt-4-turbo-preview",
                 google_access_token: Optional[str] = None):
        """Initialize the construction agent."""
        self.api_key = api_key
        self.model_name = model_name
        self.google_access_token = google_access_token
        self.graph = self._create_graph()

    def _create_tools(self) -> List[Dict[str, Any]]:
        """Create the tools for the agent."""
        tools = []
        
        if self.google_access_token:
            sheets_service = GoogleSheetsService(self.google_access_token)
            
            @tool
            async def read_google_sheet(range_name: str) -> Dict[str, Any]:
                """Tool for reading from Google Sheets."""
                try:
                    data = await sheets_service.read_sheet_data(
                        self.spreadsheet_id, 
                        range_name
                    )
                    return {"data": data}
                except Exception as e:
                    return {"error": str(e)}

            @tool
            async def write_google_sheet(
                range_name: str, 
                values: List[List[Any]], 
                is_append: bool = False
            ) -> Dict[str, Any]:
                """Tool for writing to Google Sheets."""
                try:
                    if is_append:
                        result = await sheets_service.append_sheet_data(
                            self.spreadsheet_id,
                            range_name,
                            values
                        )
                    else:
                        result = await sheets_service.write_sheet_data(
                            self.spreadsheet_id,
                            range_name,
                            values
                        )
                    return {"result": result}
                except Exception as e:
                    return {"error": str(e)}

            tools.extend([read_google_sheet, write_google_sheet])
        
        return tools

    def _create_graph(self) -> Graph:
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
        async def agent_node(state: AgentState) -> Dict:
            """Process messages and generate responses."""
            # Get the last message
            messages = state["messages"]
            # Generate response
            response = await llm_with_tools.ainvoke(messages)
            # Return updated state
            return {"messages": [response]}
        
        # Add nodes to the graph
        workflow.add_node("agent", agent_node)
        
        # Set the entrypoint from START to agent
        workflow.add_edge(START, "agent")
        
        if tools:
            # Create tool node
            tool_node = ToolNode(tools)
            workflow.add_node("tools", tool_node)
            
            # Add conditional edges
            workflow.add_conditional_edges(
                "agent",
                lambda x: "tools" if x.get("tool_calls") else END,
                {
                    "tools": "agent",
                    END: END
                }
            )
        else:
            # If no tools, just go straight to END
            workflow.add_edge("agent", END)
        
        # Compile the graph
        return workflow.compile()

    async def process_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        # Create initial state
        state = AgentState(
            messages=[HumanMessage(content=message)],
            google_access_token=self.google_access_token,
            spreadsheet_id=spreadsheet_id
        )
        
        # Run the graph
        result = await self.graph.ainvoke(state)
        
        # Extract the final message
        final_message = result["messages"][-1]
        return {
            "text": final_message.content,
            "tool_calls": getattr(final_message, "tool_calls", None)
        }

    async def process_message_stream(
        self, 
        message: str,
        conversation_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """Process a message and yield chunks of the response as they're generated."""
        logger.info("Starting message stream processing")
        # Create initial state
        state = AgentState(
            messages=[HumanMessage(content=message)],
            google_access_token=self.google_access_token,
            spreadsheet_id=spreadsheet_id   
        )
        
        logger.info("Starting graph streaming")
        # Stream the response with both messages and updates modes
        async for stream_type, event in self.graph.astream(state, stream_mode=["messages"]):
            #logger.info(f"Received event of type {stream_type}")
            #logger.info(f"Event: {event}")

            if stream_type == "messages":
                message, metadata = event
                if hasattr(message, 'content'):
                    chunk = {
                        "text": message.content,
                        "tool_calls": getattr(message, "tool_calls", None),
                        "type": "message"
                    }
                    logger.info(f"Yielding message chunk: {chunk['text'][:50]}...")
                    yield chunk
            elif stream_type == "updates" and "tool_calls" in event:
                chunk = {
                    "tool_calls": event["tool_calls"],
                    "type": "tool_call"
                }
                logger.info(f"Yielding tool call chunk: {json.dumps(chunk['tool_calls'])}")
                yield chunk
                
        logger.info("Message stream processing completed") 