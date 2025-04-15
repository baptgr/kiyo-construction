"""Extract the data from a Google Sheet in a format suited for evaluation."""

from typing import Dict, Any

def extract_template_1(sheet_id: str) -> Dict[str, Any]:
    """Extract the data from template-1."""
    return {}

EXTRACTION_FUNCTIONS = {
    "template-1": extract_template_1,
}