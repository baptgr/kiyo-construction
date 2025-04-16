"""Register data extraction functions for different template types."""

from typing import Dict, Callable, Any
from .template_1 import extract_template_1

EXTRACTION_FUNCTIONS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "template-1": extract_template_1,
} 