"""Extract data from template-1 format."""

from typing import Dict, Any, List, Optional
import logging
from leveling.modules.kiyo_agents.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)

def clean_currency_value(value: str) -> Optional[float]:
    """Clean a currency value string and convert it to float.
    
    Args:
        value: String containing a currency value
        
    Returns:
        Float value or None if conversion fails
    """
    if not value:
        return None
        
    try:
        # Remove currency symbol, spaces, and non-breaking spaces
        cleaned = value.replace('$', '').replace(' ', '').replace('\u202f', '').replace(',', '.')
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def safe_get_cell(data: List[List[Any]], row_idx: int, col_idx: int, default: Optional[Any] = None) -> Any:
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

def extract_template_1(spreadsheet_id: str, access_token: str, range_name: str = "Bid Comparison!A1:U34") -> Dict[str, Any]:
    """Extract data from template-1 format.
    
    Args:
        spreadsheet_id: ID of the Google Spreadsheet
        access_token: Google OAuth access token with Sheets scope
        range_name: Range to read in A1 notation (default: "Bid Comparison!A1:U34")
        
    Returns:
        Dict containing structured sheet data
    """
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
    
    # Extract supplier names from row 1 (looking at the header cells)
    supplier_names = []
    
    # Start from column 3 (where first supplier name is) and step by 3
    for col in range(3, len(raw_data[1]) if len(raw_data) > 0 else 0, 3):
        name = safe_get_cell(raw_data, 1, col)
        if name and name.strip() and name != "PRICE" and "[BID NAME" not in name:  # Skip column headers
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
            "name": safe_get_cell(raw_data, row_idx, 1),
            "description": safe_get_cell(raw_data, row_idx, 2),
            "bids": []
        }
        
        logger.debug(f"Processing item at row {row_idx + 1}: {item['name']}")
        
        # Process bids for each supplier
        for supplier_idx, supplier_name in enumerate(supplier_names):
            base_col = 3 + (supplier_idx * 3)
            
            # Extract raw values first for logging
            raw_price = safe_get_cell(raw_data, row_idx, base_col)
            raw_qty = safe_get_cell(raw_data, row_idx, base_col + 1)
            raw_total = safe_get_cell(raw_data, row_idx, base_col + 2)
            
            logger.debug(f"Raw values for {supplier_name}: price={raw_price}, qty={raw_qty}, total={raw_total}")
            
            try:
                # Process price
                price = clean_currency_value(raw_price)
                
                # Process quantity
                quantity = clean_currency_value(raw_qty)
                
                # Process total
                total = clean_currency_value(raw_total)
                
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
                
            except Exception as e:
                logger.error(f"Error processing bid data for supplier {supplier_name} at row {row_idx + 1}: {str(e)}", exc_info=True)
                
        if item["bids"]:  # Only append items that have bids
            structured_data["items"].append(item)
            logger.debug(f"Added item {item['name']} with {len(item['bids'])} bids")
        else:
            logger.debug(f"Skipped item {item['name']} as it had no bids")

    # Process totals for each supplier
    if len(raw_data) >= 31:  # Make sure we have enough rows
        for supplier_idx, supplier_name in enumerate(supplier_names):
            # Each supplier has 3 columns (price, quantity, total)
            # The totals are in the last column of each block
            col_start = 3 + (supplier_idx * 3)  # Start of supplier's block
            total_col = col_start + 2  # Last column of the block (total column)
            
            try:
                structured_data["totals"]["by_supplier"][supplier_name] = {
                    "subtotal": clean_currency_value(safe_get_cell(raw_data, 26, total_col)),
                    "tax_rate": clean_currency_value(safe_get_cell(raw_data, 27, total_col)),
                    "tax_amount": clean_currency_value(safe_get_cell(raw_data, 28, total_col)),
                    "shipping": clean_currency_value(safe_get_cell(raw_data, 29, total_col)),
                    "final_total": clean_currency_value(safe_get_cell(raw_data, 30, total_col))
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