import asyncio
from agents import Agent, Runner, Tool
import inspect

def print_module_contents():
    """Print the available classes and functions in the agents module"""
    import agents
    print("Available in agents module:")
    for name in dir(agents):
        if not name.startswith('_'):  # Skip private members
            item = getattr(agents, name)
            if inspect.isclass(item) or inspect.isfunction(item):
                print(f"  {name}: {type(item)}")

async def test_session_state():
    """Test how session state is handled in the OpenAI Agents SDK"""
    # Print the module contents to see what's available
    print_module_contents()
    
    # Create a simple tool to test session state
    def hello_tool(params, **kwargs):
        # Print all the arguments received by the tool
        print("\nTool arguments:")
        for key, value in kwargs.items():
            print(f"  {key}: {value}")
        
        # Check if there's context/session data
        # This will help us understand what the correct parameter name is
        return {"message": "Hello from tool!"}
    
    hello = Tool(
        name="hello",
        description="Says hello",
        schema={"type": "object", "properties": {}},
        handler=hello_tool
    )
    
    # Create an agent with this tool
    agent = Agent(
        name="Test Agent",
        instructions="You are a test agent. Use the hello tool.",
        tools=[hello]
    )
    
    # Try different ways to pass session state
    try:
        # Approach 1: Pass as named parameter
        print("\nApproach 1: Pass as session_state parameter")
        session_data = {"user_data": {"name": "Test User"}}
        result = await Runner.run(agent, "Say hello", session_state=session_data)
        print(f"Result: {result.final_output}")
    except Exception as e:
        print(f"Error with approach 1: {e}")
    
    try:
        # Approach 2: Pass as kwargs
        print("\nApproach 2: Pass as kwargs")
        session_data = {"user_data": {"name": "Test User"}}
        result = await Runner.run(agent, "Say hello", **session_data)
        print(f"Result: {result.final_output}")
    except Exception as e:
        print(f"Error with approach 2: {e}")
    
    try:
        # Approach 3: Check API reference for other parameter names
        print("\nApproach 3: Pass as context parameter")
        session_data = {"user_data": {"name": "Test User"}}
        result = await Runner.run(agent, "Say hello", context=session_data)
        print(f"Result: {result.final_output}")
    except Exception as e:
        print(f"Error with approach 3: {e}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_session_state()) 