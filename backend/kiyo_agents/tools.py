import logging

logger = logging.getLogger(__name__)

from typing import List, Dict, Any, Optional, Annotated
from langchain.tools import tool
from langchain_core.tools import InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from .google_sheets_service import GoogleSheetsService

def create_google_sheets_tools(sheets_service: GoogleSheetsService, spreadsheet_id: str) -> List[Dict[str, Any]]:
    """Create Google Sheets related tools with proper error handling and state updates."""

    logger.info(f"Creating Google Sheets tools for spreadsheet: {spreadsheet_id}")
    
    @tool
    def read_google_sheet(
        range_name: str,
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
        """Tool for reading from Google Sheets.
        
        Args:
            range_name: The A1 notation of the range to read (e.g., 'Sheet1!A1:D10')
            tool_call_id: Automatically injected tool call ID
            
        Returns:
            Command object with state update including the tool message
        """
        logger.info(f"Reading from Google Sheets: {spreadsheet_id} - {range_name}")

        try:
            data = sheets_service.read_sheet_data(
                spreadsheet_id, 
                range_name
            )
            # Format data for better readability
            formatted_data = str(data) if isinstance(data, (str, int, float)) else str(data)
            
            # Create a ToolMessage for the response
            tool_message = ToolMessage(
                content=formatted_data,
                tool_call_id=tool_call_id,
                status="success"
            )
            
            # Return a Command to update state with message
            return Command(
                update={
                    "messages": [tool_message]
                }
            )
        except Exception as e:
            error_msg = f"Error reading from Google Sheets: {str(e)}"
            logger.error(error_msg)
            
            # Create error tool message
            tool_message = ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id,
                status="error"
            )
            
            return Command(
                update={
                    "messages": [tool_message]
                }
            )

    @tool
    def write_google_sheet(
        range_name: str, 
        values: List[List[Any]], 
        tool_call_id: Annotated[str, InjectedToolCallId],
        is_append: bool = False
    ) -> Command:
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
                result = sheets_service.append_sheet_data(
                    spreadsheet_id,
                    range_name,
                    values
                )
                success_msg = f"Successfully appended data to {range_name}"
            else:
                result = sheets_service.write_sheet_data(
                    spreadsheet_id,
                    range_name,
                    values
                )
                success_msg = f"Successfully wrote data to {range_name}"
            
            # Create success tool message
            tool_message = ToolMessage(
                content=success_msg,
                tool_call_id=tool_call_id,
                status="success"
            )
            
            return Command(
                update={
                    "messages": [tool_message]
                }
            )
        except Exception as e:
            error_msg = f"Error writing to Google Sheets: {str(e)}"
            logger.error(error_msg)
            
            # Create error tool message
            tool_message = ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id,
                status="error"
            )
            
            return Command(
                update={
                    "messages": [tool_message]
                }
            )

    @tool
    def get_sheet_names(
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
        """Tool for retrieving sheet names from Google Sheets.
        
        Args:
            tool_call_id: Automatically injected tool call ID
            
        Returns:
            Command object with state update including the tool message
        """
        logger.info(f"Retrieving sheet names for spreadsheet: {spreadsheet_id}")

        try:
            # Retrieve the spreadsheet metadata
            sheet_metadata = sheets_service.get_spreadsheet_metadata(spreadsheet_id)
            
            # Extract sheet names
            sheets = sheet_metadata.get('sheets', [])
            sheet_names = [sheet.get("properties", {}).get("title", "Sheet1") for sheet in sheets]
            
            # Create a ToolMessage for the response
            tool_message = ToolMessage(
                content=f"Sheet names: {sheet_names}",
                tool_call_id=tool_call_id,
                status="success"
            )
            
            # Return a Command to update state with message
            return Command(
                update={
                    "messages": [tool_message],
                    "sheet_names": sheet_names  # Store sheet names in the state
                }
            )
        except Exception as e:
            error_msg = f"Error retrieving sheet names: {str(e)}"
            logger.error(error_msg)
            
            # Create error tool message
            tool_message = ToolMessage(
                content=error_msg,
                tool_call_id=tool_call_id,
                status="error"
            )
            
            return Command(
                update={
                    "messages": [tool_message]
                }
            )

    tools = [read_google_sheet, write_google_sheet, get_sheet_names]
    return tools 