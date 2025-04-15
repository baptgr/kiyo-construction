from typing import Dict, Any

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
        evaluator_more_than_2_words,
    ],
}