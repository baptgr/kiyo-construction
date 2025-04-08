from typing import List, Dict, Any, Optional, Annotated
from langchain.tools import tool
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from .google_sheets_service import GoogleSheetsService

def create_google_sheets_tools(sheets_service: GoogleSheetsService, spreadsheet_id: str) -> List[Dict[str, Any]]:
    """Create Google Sheets related tools with proper error handling and state updates."""
    
    @tool
    async def read_google_sheet(
        range_name: str,
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Dict[str, Any]:
        """Tool for reading from Google Sheets.
        
        Args:
            range_name: The A1 notation of the range to read (e.g., 'Sheet1!A1:D10')
            tool_call_id: Automatically injected tool call ID
            
        Returns:
            Command object with state update including the tool message
        """
        try:
            data = await sheets_service.read_sheet_data(
                spreadsheet_id, 
                range_name
            )
            # Create a ToolMessage for the response
            tool_message = ToolMessage(
                content=str(data),
                tool_call_id=tool_call_id,
                name="read_google_sheet"
            )
            # Return a Command to update state with message
            return Command(
                update={
                    "messages": [tool_message]
                }
            )
        except Exception as e:
            error_msg = f"Error reading from Google Sheets: {str(e)}"
            tool_message = ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id,
                name="read_google_sheet",
                status="error"
            )
            return Command(
                update={
                    "error": str(e),
                    "messages": [tool_message]
                }
            )

    @tool
    async def write_google_sheet(
        range_name: str, 
        values: List[List[Any]], 
        tool_call_id: Annotated[str, InjectedToolCallId],
        is_append: bool = False
    ) -> Dict[str, Any]:
        """Tool for writing to Google Sheets.
        
        Args:
            range_name: The A1 notation of the range to write to (e.g., 'Sheet1!A1')
            values: 2D array of values to write
            tool_call_id: Automatically injected tool call ID
            is_append: If True, appends data. If False, overwrites data.
            
        Returns:
            Command object with state update including the tool message
        """
        try:
            if is_append:
                result = await sheets_service.append_sheet_data(
                    spreadsheet_id,
                    range_name,
                    values
                )
            else:
                result = await sheets_service.write_sheet_data(
                    spreadsheet_id,
                    range_name,
                    values
                )
            success_msg = f"Successfully {'appended' if is_append else 'wrote'} data to {range_name}"
            tool_message = ToolMessage(
                content=success_msg,
                tool_call_id=tool_call_id,
                name="write_google_sheet"
            )
            return Command(
                update={
                    "messages": [tool_message]
                }
            )
        except Exception as e:
            error_msg = f"Error writing to Google Sheets: {str(e)}"
            tool_message = ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id,
                name="write_google_sheet",
                status="error"
            )
            return Command(
                update={
                    "error": str(e),
                    "messages": [tool_message]
                }
            )

    return [read_google_sheet, write_google_sheet] 