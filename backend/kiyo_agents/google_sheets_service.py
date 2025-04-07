import os
import json
import httpx
from typing import List, Dict, Any, Optional
import logging

class GoogleSheetsService:
    """
    Service for interacting with Google Sheets API.
    
    This service provides methods to read and write data to Google Sheets,
    which will be used by the agent's tools.
    """
    
    def __init__(self, access_token: str):
        """
        Initialize the Google Sheets service with an access token.
        
        Args:
            access_token: Google OAuth access token with Sheets scope
        """
        self.access_token = access_token
        self.base_url = "https://sheets.googleapis.com/v4/spreadsheets"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    async def read_sheet_data(
        self, 
        spreadsheet_id: str, 
        range_name: str
    ) -> List[List[Any]]:
        """
        Read data from a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to read (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of rows, where each row is a list of values
        """
        try:
            url = f"{self.base_url}/{spreadsheet_id}/values/{range_name}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                return data.get("values", [])
        except Exception as e:
            raise Exception(f"Error reading Google Sheet: {str(e)}")
    
    async def write_sheet_data(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> Dict[str, Any]:
        """
        Write data to a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to update (e.g., 'Sheet1!A1:D10')
            values: List of rows to write, where each row is a list of values
            value_input_option: How to interpret input data
                "RAW": The values will not be parsed
                "USER_ENTERED": As if they were entered in the UI
                
        Returns:
            Response from the update API call
        """
        try:
            # Debug logging for request parameters
            logger = logging.getLogger(__name__)
            logger.info(f"Attempting to write to spreadsheet ID: {spreadsheet_id}")
            logger.info(f"Range: {range_name}")
            logger.info(f"Value input option: {value_input_option}")
            logger.info(f"Data structure: {type(values)}, rows: {len(values)}, first row type: {type(values[0]) if values and len(values) > 0 else 'N/A'}")
            logger.info(f"First few values: {str(values)[:200]}...")
            
            # Check token validity (without logging the full token)
            token_prefix = self.access_token[:5] if self.access_token else "None"
            token_length = len(self.access_token) if self.access_token else 0
            logger.info(f"Using access token: {token_prefix}... (length: {token_length})")
            
            url = f"{self.base_url}/{spreadsheet_id}/values/{range_name}"
            logger.info(f"Request URL: {url}")
            
            body = {
                "values": values,
                "majorDimension": "ROWS"
            }
            
            params = {
                "valueInputOption": value_input_option
            }
            
            async with httpx.AsyncClient() as client:
                logger.info("Sending request to Google Sheets API...")
                response = await client.put(
                    url, 
                    headers=self.headers, 
                    params=params,
                    json=body
                )
                
                logger.info(f"Response status: {response.status_code}")
                if not response.is_success:
                    response_text = response.text
                    logger.error(f"Error response from Google Sheets API: {response_text}")
                    
                    # Try to parse the error message to get more detailed information
                    try:
                        error_json = response.json()
                        if 'error' in error_json and 'message' in error_json['error']:
                            detailed_message = error_json['error']['message']
                            raise Exception(f"Google Sheets API error: {detailed_message}")
                    except (json.JSONDecodeError, KeyError):
                        pass
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"Write successful. Updated cells: {result.get('updatedCells', 0)}")
                return result
        except Exception as e:
            logger.error(f"Error writing to Google Sheet: {str(e)}", exc_info=True)
            raise Exception(f"Error writing to Google Sheet: {str(e)}")
    
    async def append_sheet_data(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[List[Any]],
        value_input_option: str = "USER_ENTERED"
    ) -> Dict[str, Any]:
        """
        Append data to a Google Sheet.
        
        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The A1 notation of the range to append after
            values: List of rows to append, where each row is a list of values
            value_input_option: How to interpret input data
                
        Returns:
            Response from the append API call
        """
        try:
            # Debug logging for request parameters
            logger = logging.getLogger(__name__)
            logger.info(f"Attempting to append to spreadsheet ID: {spreadsheet_id}")
            logger.info(f"Range: {range_name}")
            logger.info(f"Value input option: {value_input_option}")
            logger.info(f"Data structure: {type(values)}, rows: {len(values)}, first row type: {type(values[0]) if values and len(values) > 0 else 'N/A'}")
            logger.info(f"First few values: {str(values)[:200]}...")
            
            # Check token validity (without logging the full token)
            token_prefix = self.access_token[:5] if self.access_token else "None"
            token_length = len(self.access_token) if self.access_token else 0
            logger.info(f"Using access token: {token_prefix}... (length: {token_length})")
            
            url = f"{self.base_url}/{spreadsheet_id}/values/{range_name}:append"
            logger.info(f"Request URL: {url}")
            
            body = {
                "values": values,
                "majorDimension": "ROWS"
            }
            
            params = {
                "valueInputOption": value_input_option,
                "insertDataOption": "INSERT_ROWS"
            }
            
            async with httpx.AsyncClient() as client:
                logger.info("Sending append request to Google Sheets API...")
                response = await client.post(
                    url, 
                    headers=self.headers, 
                    params=params,
                    json=body
                )
                
                logger.info(f"Response status: {response.status_code}")
                if not response.is_success:
                    response_text = response.text
                    logger.error(f"Error response from Google Sheets API: {response_text}")
                    
                    # Try to parse the error message to get more detailed information
                    try:
                        error_json = response.json()
                        if 'error' in error_json and 'message' in error_json['error']:
                            detailed_message = error_json['error']['message']
                            raise Exception(f"Google Sheets API error: {detailed_message}")
                    except (json.JSONDecodeError, KeyError):
                        pass
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"Append successful. Updated cells: {result.get('updates', {}).get('updatedCells', 0)}")
                return result
        except Exception as e:
            logger.error(f"Error appending to Google Sheet: {str(e)}", exc_info=True)
            raise Exception(f"Error appending to Google Sheet: {str(e)}") 