#!/usr/bin/env python
"""
Test script to check if the word duplication happens directly in the OpenAI Agents SDK.
This uses the SDK directly with minimal wrapping to isolate the issue.
"""

import asyncio
import os
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

# Load environment variables (for API key)
load_dotenv()

# Import the OpenAI Agents SDK
from agents import Agent, Runner

async def test_streaming():
    """Test streaming with minimal wrapping to check for duplication."""
    # Create a simple agent
    agent = Agent(
        name="Construction Assistant",
        instructions="You are an AI assistant for a construction company. Be helpful and concise."
    )
    
    # Get a streamed response
    message = "Tell me about different types of building materials."
    print(f"\nSending message: '{message}'\n")
    print("------ RAW CHUNKS FROM SDK ------")
    
    result = Runner.run_streamed(agent, input=message)
    
    # Stream and collect the response
    full_response = ""
    chunk_count = 0
    
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            chunk = event.data.delta
            full_response += chunk
            chunk_count += 1
            
            # Print each chunk separately to see if duplications are in the raw chunks
            print(f"CHUNK {chunk_count} ({len(chunk)} chars): '{chunk}'")
    
    # Analyze the response
    print("\n------ ANALYSIS ------")
    print(f"Total chunks received: {chunk_count}")
    print(f"Total response length: {len(full_response)} characters")
    
    # Check for word duplication pattern
    words = full_response.split()
    duplicate_count = 0
    
    for i in range(len(words) - 1):
        if words[i] == words[i + 1]:
            duplicate_count += 1
            print(f"Found duplicate words: '{words[i]}' (positions {i} and {i+1})")
    
    print(f"\nFound {duplicate_count} duplicate word pairs")
    
    # Print full response
    print("\n------ FULL RESPONSE ------")
    print(full_response)

if __name__ == "__main__":
    asyncio.run(test_streaming()) 