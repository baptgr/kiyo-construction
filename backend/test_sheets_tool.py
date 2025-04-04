import asyncio
import os
import json
import sys
from kiyo_agents.construction_agent import ConstructionAgentFactory

async def test_google_sheets_tools():
    """
    Test the Google Sheets tools with a sample spreadsheet.
    
    Usage:
        python test_sheets_tool.py <access_token> <spreadsheet_id>
    """
    if len(sys.argv) < 3:
        print("Usage: python test_sheets_tool.py <access_token> <spreadsheet_id>")
        return
    
    google_token = sys.argv[1]
    spreadsheet_id = sys.argv[2]
    
    print(f"Testing with spreadsheet ID: {spreadsheet_id}")
    
    # Create an agent with Google access token
    factory = ConstructionAgentFactory(
        api_key=os.environ.get('OPENAI_API_KEY'),
        google_access_token=google_token
    )
    agent = factory.create_agent()
    
    # First test: Try to read the spreadsheet
    print("\n--- Testing read operation ---")
    read_prompt = f"Read data from Google Sheet with ID {spreadsheet_id} from range Sheet1!A1:C5"
    read_response = await agent.process_message(read_prompt)
    print(f"Agent response:\n{read_response['text']}")
    
    # Second test: Try to write to the spreadsheet
    print("\n--- Testing write operation ---")
    write_prompt = (
        f"Write the following data to Google Sheet with ID {spreadsheet_id} in range Sheet1!E1:F3: "
        f"[['Item', 'Price'], ['Concrete', '85.00'], ['Steel', '120.00']]"
    )
    write_response = await agent.process_message(write_prompt)
    print(f"Agent response:\n{write_response['text']}")
    
    # Third test: Try to append to the spreadsheet
    print("\n--- Testing append operation ---")
    append_prompt = (
        f"Append this data to Google Sheet with ID {spreadsheet_id} in range Sheet1!A:B using is_append=true: "
        f"[['New Item', 'New Description']]"
    )
    append_response = await agent.process_message(append_prompt)
    print(f"Agent response:\n{append_response['text']}")

if __name__ == "__main__":
    asyncio.run(test_google_sheets_tools()) 