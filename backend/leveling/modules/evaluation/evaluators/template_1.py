from typing import Dict, Any

def evaluator_empty_cells_compliance(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if the spreadsheet maintains required empty cells.
    
    Args:
        inputs: Dictionary containing the input message
        outputs: Dictionary containing the output data
        
    Returns:
        Dictionary containing the score and details
    """
    data = outputs["data"]
    empty_validations = data["empty_validations"]
    score = 1
    details = []
    
    # Check first row compliance with exception
    first_row_content = empty_validations["first_row"]["content"]
    if any(content and content != "BID COMPARISON TEMPLATE" for content in first_row_content):
        score = 0
        details.append("First row contains unexpected content")
    
    # Check first column compliance
    if any(empty_validations["first_column"]["content"]):
        score = 0
        details.append("First column contains non-empty cells")
    
    # Check rows after 32 compliance with exception
    rows_after_32_content = empty_validations["rows_after_32"]["content"]
    if any(any(content and content != "CLICK HERE TO CREATE IN SMARTSHEET" for content in row) for row in rows_after_32_content):
        score = 0
        details.append("Rows after 32 contain unexpected content")
    
    # Check columns after U compliance
    if any(any(col) for col in empty_validations["columns_after_U"]["content"]):
        score = 0
        details.append("Columns after U contain non-empty cells")
    
    # Check title whitespace compliance
    if any(empty_validations["title_whitespace"]["content"]):
        score = 0
        details.append("Title whitespace cells contain non-empty values")
    
    return {
        "score": score,
        "details": details
    }

def evaluator_formula_compliance(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if the spreadsheet maintains required formulas.
    
    Args:
        inputs: Dictionary containing the input message
        outputs: Dictionary containing the output data
        
    Returns:
        Dictionary containing the score and details
    """
    data = outputs["data"]
    formula_validations = data["formula_validations"]
    score = 1
    details = []
    
    def is_valid_formula(formula):
        if not formula:
            return False
        if not isinstance(formula, str):
            return False
        return formula.startswith("=")
    
    # Check item totals formulas
    for cell, formula in formula_validations["item_totals"]["cells"].items():
        if not is_valid_formula(formula):
            score = 0
            details.append(f"Missing or invalid formula in cell {cell}")
    
    # Check subtotals formulas
    for cell, formula in formula_validations["subtotals"]["cells"].items():
        if not is_valid_formula(formula):
            score = 0
            details.append(f"Missing or invalid formula in cell {cell}")
    
    # Check tax totals formulas
    for cell, formula in formula_validations["tax_totals"]["cells"].items():
        if not is_valid_formula(formula):
            score = 0
            details.append(f"Missing or invalid formula in cell {cell}")
    
    # Check final totals formulas
    for cell, formula in formula_validations["final_totals"]["cells"].items():
        if not is_valid_formula(formula):
            score = 0
            details.append(f"Missing or invalid formula in cell {cell}")
    
    return {
        "score": score,
        "details": details
    }

def evaluator_item_completeness(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if all required item fields are filled.
    
    Args:
        inputs: Dictionary containing the input message
        outputs: Dictionary containing the output data
        
    Returns:
        Dictionary containing the score and details
    """
    data = outputs["data"]
    items = data["items"]
    score = 1
    details = []
    
    for item in items:
        # Check name and description
        if not item["name"]:
            score = 0
            details.append(f"Missing name for item at row {item['row_index']}")
        
        # Check bids for each supplier
        for bid in item["bids"]:
            if bid["price"] is None:
                score = 0
                details.append(f"Missing price for {bid['supplier']} in item at row {item['row_index']}")
            if bid["quantity"] is None:
                score = 0
                details.append(f"Missing quantity for {bid['supplier']} in item at row {item['row_index']}")
            
            # Check if price and quantity are numbers
            if bid["price"] is not None and not isinstance(bid["price"], (int, float)):
                score = 0
                details.append(f"Invalid price format for {bid['supplier']} in item at row {item['row_index']}")
            if bid["quantity"] is not None and not isinstance(bid["quantity"], (int, float)):
                score = 0
                details.append(f"Invalid quantity format for {bid['supplier']} in item at row {item['row_index']}")
    
    return {
        "score": score,
        "details": details
    }

def evaluator_supplier_count(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if the number of suppliers matches the number of PDFs provided.
    
    Args:
        inputs: Dictionary containing the input message and PDF paths
        outputs: Dictionary containing the output data
        
    Returns:
        Dictionary containing the score and details
    """
    data = outputs["data"]
    expected_supplier_count = len(inputs["pdf_paths"])
    actual_supplier_count = len(data["totals"]["by_supplier"])
    
    score = 1 if expected_supplier_count == actual_supplier_count else 0
    details = []
    
    if score == 0:
        details.append(
            f"Expected {expected_supplier_count} suppliers (based on PDF count) but found {actual_supplier_count} suppliers"
        )
    
    return {
        "score": score,
        "details": details
    }