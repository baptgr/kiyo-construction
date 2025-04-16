from typing import Dict, Any

from .template_1 import (
    evaluator_empty_cells_compliance,
    evaluator_formula_compliance,
    evaluator_item_completeness,
    evaluator_supplier_count
)

# This is an example
def evaluator_more_than_2_words(inputs: Dict[str, Any], outputs: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate if the response has more than 2 words.
    
    Args:
        inputs: Dictionary containing the input message
        outputs: Dictionary containing the output response
        
    Returns:
        Dictionary containing the score
    """
    words = outputs["response"]["text"].split()
    return {"score": 1 if len(words) > 2 else 0}

EVALUATORS_FUNCTIONS = {
    "template-1": [
        evaluator_empty_cells_compliance,
        evaluator_formula_compliance,
        evaluator_item_completeness, 
        evaluator_supplier_count
    ],
}