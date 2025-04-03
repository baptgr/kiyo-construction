#!/usr/bin/env python
"""
Minimal test script using the example from GitHub
"""

import asyncio
import os
import sys

# Add parent directory to path to avoid conflict with local modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from the agents package
from agents import Agent, Runner

async def main():
    # Make sure OpenAI API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("WARNING: OPENAI_API_KEY environment variable not set")
    else:
        print(f"Using API key: {api_key[:5]}...")
        
    print("Creating agent...")
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )
    
    print("Running agent...")
    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print("Result:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main()) 