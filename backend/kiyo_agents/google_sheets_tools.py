import json
from typing import Dict, List, Any, Optional
from .google_sheets_service import GoogleSheetsService
from agents import FunctionTool, RunContextWrapper
import logging

logger = logging.getLogger(__name__)

# JSON Schema for the read_sheet tool
READ_SHEET_SCHEMA = {
    "type": "object",
    "properties": {
        "spreadsheet_id": {
            "type": "string",
            "description": "The ID of the Google Sheet to read from"
        },
        "range": {
            "type": "string",
            "description": "The A1 notation range to read (e.g., 'Sheet1!A1:D10')"
        }
    },
    "required": ["spreadsheet_id", "range"],
    "additionalProperties": False
}

# JSON Schema for the write_sheet tool
WRITE_SHEET_SCHEMA = {
    "type": "object",
    "properties": {
        "spreadsheet_id": {
            "type": "string",
            "description": "The ID of the Google Sheet to write to"
        },
        "range": {
            "type": "string",
            "description": "The A1 notation range to write to (e.g., 'Sheet1!A1:D10')"
        },
        "values": {
            "type": "array",
            "description": "2D array of values to write to the sheet",
            "items": {
                "type": "array",
                "items": {
                    "type": ["string", "number", "boolean", "null"],
                    "description": "Cell value (string, number, boolean, or null)"
                }
            }
        },
        "is_append": {
            "type": "boolean",
            "description": "Whether to append data after existing content (true) or overwrite the range (false)"
        }
    },
    "required": ["spreadsheet_id", "range", "values", "is_append"],
    "additionalProperties": False
}

def get_access_token(ctx: RunContextWrapper[Any]) -> Optional[str]:
    """
    Extract Google access token from context wrapper.
    This is a fallback method - direct token passing is preferred.
    
    Args:
        ctx: The run context wrapper
        
    Returns:
        Access token string or None if not available
    """
    # Try all possible locations where the token might be stored
    locations_to_check = []
    
    # 1. Check if context is a direct attribute with dictionary value
    if hasattr(ctx, "context") and isinstance(ctx.context, dict):
        locations_to_check.append(("ctx.context", ctx.context))
    
    # 2. Check for direct access to field
    if hasattr(ctx, "google_access_token"):
        return getattr(ctx, "google_access_token")
        
    # 3. Check if ctx has user_info
    if hasattr(ctx, "user_info") and isinstance(ctx.user_info, dict):
        locations_to_check.append(("ctx.user_info", ctx.user_info))
        
    # 4. Check if ctx has kwargs
    if hasattr(ctx, "kwargs") and isinstance(ctx.kwargs, dict):
        locations_to_check.append(("ctx.kwargs", ctx.kwargs))
    
    # Check all collected locations
    for location_name, location_dict in locations_to_check:
        if "google_access_token" in location_dict:
            return location_dict.get("google_access_token")
    
    # No token found
    return None

async def read_sheet_tool(ctx: RunContextWrapper[Any], args: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool for reading data from a Google Sheet.
    
    Args:
        ctx: The run context wrapper
        args: JSON string of parameters
        token: Optional pre-configured access token
        
    Returns:
        Dictionary containing the data read from the sheet
    """
    # Parse arguments from JSON string
    params = json.loads(args)
    
    # Use provided token or try to get from context
    access_token = token
    if not access_token:
        access_token = get_access_token(ctx)
    
    try:
        spreadsheet_id = params.get("spreadsheet_id")
        range_name = params.get("range")
        
        # Create Google Sheets service
        sheets_service = GoogleSheetsService(access_token)
        
        # Read data from the spreadsheet
        values = await sheets_service.read_sheet_data(spreadsheet_id, range_name)
        
        # Return the data
        return {
            "data": values,
            "rows": len(values),
            "columns": len(values[0]) if values else 0
        }
    except Exception as e:
        return {
            "error": f"Failed to read sheet: {str(e)}"
        }

async def write_sheet_tool(ctx: RunContextWrapper[Any], args: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Tool for writing data to a Google Sheet.
    
    Args:
        ctx: The run context wrapper
        args: JSON string of parameters
        token: Optional pre-configured access token
        
    Returns:
        Dictionary containing the result of the write operation
    """
    # Parse arguments from JSON string
    params = json.loads(args)
    
    # Use provided token or try to get from context
    access_token = token
    if not access_token:
        access_token = get_access_token(ctx)
    
    try:
        spreadsheet_id = params.get("spreadsheet_id")
        range_name = params.get("range")
        values = params.get("values")
        is_append = params.get("is_append", False)
        
        # Create Google Sheets service
        sheets_service = GoogleSheetsService(access_token)
        
        if is_append:
            # Append data to the spreadsheet
            result = await sheets_service.append_sheet_data(
                spreadsheet_id, 
                range_name, 
                values
            )
        else:
            # Write data to the spreadsheet
            result = await sheets_service.write_sheet_data(
                spreadsheet_id, 
                range_name, 
                values
            )
        
        # Return success message
        return {
            "success": True,
            "updated_range": result.get("updatedRange", range_name),
            "updated_cells": result.get("updatedCells", 0)
        }
    except Exception as e:
        return {
            "error": f"Failed to write to sheet: {str(e)}"
        }

# Create the tool instances using FunctionTool directly
read_sheet = FunctionTool(
    name="read_google_sheet",
    description="Read data from a Google Sheet. Requires spreadsheet ID and range in A1 notation.",
    params_json_schema=READ_SHEET_SCHEMA,
    on_invoke_tool=read_sheet_tool
)

write_sheet = FunctionTool(
    name="write_google_sheet",
    description="Write data to a Google Sheet. Requires spreadsheet ID, range, and 2D array of values.",
    params_json_schema=WRITE_SHEET_SCHEMA,
    on_invoke_tool=write_sheet_tool
)

# Export the tools
google_sheets_tools = [read_sheet, write_sheet] 