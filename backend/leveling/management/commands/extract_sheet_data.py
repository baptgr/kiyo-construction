"""Extract data from a Google Sheet."""

import os
import logging
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from kiyo_agents.google_sheets_service import GoogleSheetsService
from typing import Dict, Any, List, Optional, TypeVar, Union
import json

load_dotenv()

logger = logging.getLogger(__name__)

T = TypeVar('T')

def safe_get_cell(data: List[List[Any]], row_idx: int, col_idx: int, default: Optional[T] = None) -> Union[Any, T]:
    """Safely get a cell value from a 2D array.
    
    Args:
        data: 2D array of data
        row_idx: Row index
        col_idx: Column index
        default: Default value if cell doesn't exist
        
    Returns:
        Cell value if it exists, default otherwise
    """
    try:
        if row_idx < len(data) and col_idx < len(data[row_idx]):
            return data[row_idx][col_idx]
        return default
    except (IndexError, TypeError):
        return default

def transform_sheet_data(raw_data: List[List[Any]], formula_data: List[List[Any]]) -> Dict[str, Any]:
    """Transform raw sheet data into structured format.
    
    Args:
        raw_data: List of rows from Google Sheets API
        formula_data: List of rows from Google Sheets API with formulas
        
    Returns:
        Dict containing structured sheet data
    """
    # Extract supplier names from row 2 (looking at the header cells)
    supplier_names = []
    for col in range(2, len(raw_data[1]) if len(raw_data) > 1 else 0, 3):
        name = safe_get_cell(raw_data, 1, col)
        if name and name.strip() and name != "PRICE":  # Skip column headers
            supplier_names.append(name)
    
    logger.info(f"Found suppliers: {supplier_names}")
    
    # Initialize the structure
    structured_data = {
        "metadata": {
            "sheet_name": "Bid Comparison",
            "total_suppliers": len(supplier_names),
            "supplier_names": supplier_names,
            "valid_data_range": {
                "start_row": 3,
                "end_row": 31,
                "start_col": "A",
                "end_col": "U"
            }
        },
        "empty_validations": {
            "first_row": {
                "range": "A1:U1",
                "content": raw_data[0] if raw_data else []
            },
            "first_column": {
                "range": "A1:A34",
                "content": [safe_get_cell(raw_data, i, 0) for i in range(len(raw_data))]
            },
            "rows_after_32": {
                "range": "A32:U100",
                "content": [
                    row for idx, row in enumerate(raw_data)
                    if idx >= 31  # Row 32 and beyond
                ]
            },
            "columns_after_U": {
                "range": "V1:Z100",
                "content": [
                    [cell for col_idx, cell in enumerate(row) if col_idx >= 21]
                    for row in raw_data
                ]
            },
            "title_whitespace": {
                "ranges": [
                    "E2", "F2", "H2", "I2", "K2", "L2", "N2", "O2", "Q2", "R2", "T2", "U2"
                ],
                "content": [
                    safe_get_cell(raw_data, 1, 4),  # E2
                    safe_get_cell(raw_data, 1, 5),  # F2
                    safe_get_cell(raw_data, 1, 7),  # H2
                    safe_get_cell(raw_data, 1, 8),  # I2
                    safe_get_cell(raw_data, 1, 10),  # K2
                    safe_get_cell(raw_data, 1, 11),  # L2
                    safe_get_cell(raw_data, 1, 13),  # N2
                    safe_get_cell(raw_data, 1, 14),  # O2
                    safe_get_cell(raw_data, 1, 16),  # Q2
                    safe_get_cell(raw_data, 1, 17),  # R2
                    safe_get_cell(raw_data, 1, 19),  # T2
                    safe_get_cell(raw_data, 1, 20)   # U2
                ]
            }
        },
        "formula_validations": {
            "item_totals": {
                "cells": {
                    f"{chr(ord('F') + (3 * i))}{row}": safe_get_cell(formula_data, row-1, 5 + (3 * i))
                    for i in range(5)  # For each supplier
                    for row in range(4, 27)  # Rows 4-26
                }
            },
            "subtotals": {
                "cells": {
                    f"{chr(ord('F') + (3 * i))}27": safe_get_cell(formula_data, 26, 5 + (3 * i))
                    for i in range(5)  # For each supplier
                }
            },
            "tax_totals": {
                "cells": {
                    f"{chr(ord('F') + (3 * i))}29": safe_get_cell(formula_data, 28, 5 + (3 * i))
                    for i in range(5)  # For each supplier
                }
            },
            "final_totals": {
                "cells": {
                    f"{chr(ord('F') + (3 * i))}31": safe_get_cell(formula_data, 30, 5 + (3 * i))
                    for i in range(5)  # For each supplier
                }
            }
        },
        "items": [],
        "totals": {"by_supplier": {}}
    }

    # Process items (starting from row 4 to 26)
    for row_idx in range(3, min(26, len(raw_data))):
        row = raw_data[row_idx]
        if not row or not any(row):  # Skip empty rows
            continue
            
        item = {
            "row_index": row_idx + 1,  # 1-based index
            "name": safe_get_cell(raw_data, row_idx, 0),
            "description": safe_get_cell(raw_data, row_idx, 1),
            "bids": [],
            "bids_per_item": 0  # Track number of valid bids for this item
        }
        
        logger.debug(f"Processing item at row {row_idx + 1}: {item['name']}")
        
        # Process bids for each supplier
        for supplier_idx, supplier_name in enumerate(supplier_names):
            base_col = 2 + (supplier_idx * 3)
            
            # Extract raw values first for logging
            raw_price = safe_get_cell(raw_data, row_idx, base_col)
            raw_qty = safe_get_cell(raw_data, row_idx, base_col + 1)
            raw_total = safe_get_cell(raw_data, row_idx, base_col + 2)
            
            logger.debug(f"Raw values for {supplier_name}: price={raw_price}, qty={raw_qty}, total={raw_total}")
            
            try:
                # Process price
                price = None
                if raw_price and raw_price != '-':
                    try:
                        price = float(str(raw_price).replace('$', '').replace(',', ''))
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not convert price '{raw_price}' to float: {e}")
                
                # Process quantity
                quantity = None
                if raw_qty and raw_qty != '-':
                    try:
                        quantity = float(str(raw_qty))
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not convert quantity '{raw_qty}' to float: {e}")
                
                # Process total
                total = None
                if raw_total and raw_total != '-':
                    try:
                        total = float(str(raw_total).replace('$', '').replace(',', ''))
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Could not convert total '{raw_total}' to float: {e}")
                
                bid = {
                    "supplier": supplier_name,
                    "price": price,
                    "quantity": quantity,
                    "total": total,
                    "raw_values": {  # Keep raw values for debugging
                        "price": raw_price,
                        "quantity": raw_qty,
                        "total": raw_total
                    }
                }
                
                logger.debug(f"Processed bid for {supplier_name}: {bid}")
                
                # Only append bid if it has any data
                if any(v is not None for v in [price, quantity, total]):
                    item["bids"].append(bid)
                    item["bids_per_item"] += 1
                    logger.debug(f"Added bid for {supplier_name}, total bids: {item['bids_per_item']}")
                
            except Exception as e:
                logger.error(f"Error processing bid data for supplier {supplier_name} at row {row_idx + 1}: {str(e)}", exc_info=True)
                
        if item["bids"]:  # Only append items that have bids
            structured_data["items"].append(item)
            logger.debug(f"Added item {item['name']} with {len(item['bids'])} bids")
        else:
            logger.debug(f"Skipped item {item['name']} as it had no bids")

    # Process totals for each supplier
    if len(raw_data) >= 31:  # Make sure we have enough rows
        def safe_float(val, strip_currency=True):
            if not val or val == '-':
                return None
            if strip_currency:
                val = str(val).replace('$', '').replace(',', '')
            if '%' in str(val):
                val = str(val).strip('%')
            return float(val)
            
        for supplier_idx, supplier_name in enumerate(supplier_names):
            col_start = 2 + (supplier_idx * 3)
            
            try:
                structured_data["totals"]["by_supplier"][supplier_name] = {
                    "subtotal": safe_float(safe_get_cell(formula_data, 26, col_start + 2)),
                    "tax_rate": safe_float(safe_get_cell(formula_data, 27, col_start + 2)),
                    "tax_amount": safe_float(safe_get_cell(formula_data, 28, col_start + 2)),
                    "shipping": safe_float(safe_get_cell(formula_data, 29, col_start + 2)),
                    "final_total": safe_float(safe_get_cell(formula_data, 30, col_start + 2))
                }
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error processing totals for supplier {supplier_name}: {str(e)}")
                structured_data["totals"]["by_supplier"][supplier_name] = {
                    "subtotal": None,
                    "tax_rate": None,
                    "tax_amount": None,
                    "shipping": None,
                    "final_total": None
                }

    return structured_data

class Command(BaseCommand):
    help = 'Extract data from a Google Sheet using the specified template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spreadsheet-id',
            type=str,
            required=True,
            help='The ID of the Google Spreadsheet to extract data from'
        )
        parser.add_argument(
            '--range',
            type=str,
            help='The range to read in A1 notation (e.g., Sheet1!A1:D10)',
            default='Bid Comparison!A1:U34'
        )
        parser.add_argument(
            '--access-token',
            type=str,
            help='Google OAuth access token with Sheets scope',
            default=os.getenv('DEV_GOOGLE_ACCESS_TOKEN')
        )

    def handle(self, *args, **options):
        spreadsheet_id = options['spreadsheet_id']
        range_name = options['range']
        access_token = options['access_token']

        logger.info(f"Attempting to read spreadsheet ID: {spreadsheet_id}")
        logger.info(f"Range: {range_name}")
        logger.info(f"Access token present: {'Yes' if access_token else 'No'}")

        if not access_token:
            self.stdout.write(
                self.style.ERROR('No access token provided. Please set DEV_GOOGLE_ACCESS_TOKEN in your .env file or provide it via --access-token')
            )
            return

        try:
            # Initialize Google Sheets service
            sheets_service = GoogleSheetsService(access_token=access_token)
            
            # Read data from the sheet
            raw_data = sheets_service.read_sheet_data(
                spreadsheet_id=spreadsheet_id,
                range_name=range_name
            )
            
            # Read formulas for formula cells
            formula_data = sheets_service.read_sheet_data(
                spreadsheet_id=spreadsheet_id,
                range_name=range_name,
                value_render_option="FORMULA"
            )
            
            # Transform the data into our structured format
            structured_data = transform_sheet_data(raw_data, formula_data)
            
            # Output the results
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully extracted and transformed data:\n{json.dumps(structured_data, indent=2)}'
                )
            )
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error extracting data: {error_message}", exc_info=True)
            
            if "400" in error_message:
                self.stdout.write(
                    self.style.ERROR(
                        'Bad Request (400) error. This could be due to:\n'
                        '1. Invalid spreadsheet ID\n'
                        '2. Invalid range format\n'
                        '3. Insufficient permissions\n'
                        '4. Invalid access token\n\n'
                        f'Full error: {error_message}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Error extracting data: {error_message}')
                )