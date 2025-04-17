from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict, Annotated
import logging

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, SystemMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from .google_sheets_service import GoogleSheetsService
from .tools import create_google_sheets_tools

logger = logging.getLogger(__name__)

# Global memory saver instance
_memory_saver = MemorySaver()

class AgentState(TypedDict):
    """Type definition for the agent's state"""
    messages: Annotated[List[BaseMessage], add_messages]
    google_access_token: Optional[str]
    spreadsheet_id: Optional[str]

class ConstructionAgent:
    """Implementation of the construction agent using LangGraph."""
    
    def __init__(
        self,
        api_key: str,
        google_access_token: str,
        spreadsheet_id: str,
        config: Dict[str, Any] = None
    ):
        self.api_key = api_key
        self.google_access_token = google_access_token
        self.spreadsheet_id = spreadsheet_id
        self.config = config or {"configurable": {"model": "gpt-4o", "system_instructions": "You are a helpful assistant"}}
        
        # Use the global memory saver
        self.memory = _memory_saver
        self.graph = self._create_graph()

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
        model = self._get_model()
        
        # Create tools
        tools = self._create_tools()
        
        # Bind tools to the LLM
        llm_with_tools = model.bind_tools(tools)
        
        # Create the agent node
        def agent_node(state: AgentState) -> Dict:
            """Process messages and generate responses."""
            # Prepend the system instructions to the current messages
            messages_with_instructions = [SystemMessage(content=self.config["configurable"]["system_instructions"])] + state["messages"]
            response = llm_with_tools.invoke(messages_with_instructions)
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

    def _get_model(self):
        """Get the configured model"""
        model_name = self.config["configurable"].get("model", "gpt-4o")
        # Initialize the appropriate model based on config
        if model_name in ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "o1"]:
            return ChatOpenAI(model=model_name)
        elif "claude" in model_name:
            return ChatAnthropic(model=model_name)
        else:
            raise ValueError(f"Invalid model: {model_name}")
        
    def process_message(
        self, 
        message: str, 
        conversation_id: Optional[str] = None,
        spreadsheet_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        #logger.info(f"Processing message for conversation {conversation_id}")
        
        # Get existing messages from memory if conversation_id exists
        existing_messages = []
        if conversation_id:
            try:
                # Try to get existing state from memory
                existing_state = self.memory.get_state(conversation_id)
                if existing_state and "messages" in existing_state:
                    existing_messages = existing_state["messages"]
                    #logger.info(f"Found existing messages for conversation {conversation_id}")
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
                
        #logger.info("Message stream processing completed") 