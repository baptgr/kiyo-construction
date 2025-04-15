from typing import Dict, Any, List, Callable
from langsmith import Client
from kiyo_agents.construction_agent import ConstructionAgent

from .evaluators import evaluator_more_than_2_words

def build_dataset(client: Client, dataset_name: str) -> None:
    """Create or get a dataset for evaluation.
    
    Args:
        client: LangSmith client instance
        dataset_name: Name of the dataset to create/use
    """
    try:
        # Try to get existing dataset
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"Using existing dataset: {dataset_name}")
    except:
        # Create new dataset if it doesn't exist
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Dataset for evaluating the construction agent's responses"
        )
        print(f"Created new dataset: {dataset_name}")

        # Create examples for the dataset
        examples = [
            {
                "inputs": {"message": "Hello"},
            },
            {
                "inputs": {"message": "How are you?"},
            }
        ]

        # Add examples to the dataset
        client.create_examples(dataset_id=dataset.id, examples=examples)
        print("Added examples to the dataset")

def create_target_function(agent: ConstructionAgent) -> Callable:
    """Create a target function for evaluation.
    
    Args:
        agent: ConstructionAgent instance to evaluate
    
    Returns:
        A function that takes inputs and returns outputs
    """
    def target_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message and return the response.
        
        Args:
            inputs: Dictionary containing the input message
            
        Returns:
            Dictionary containing the response
        """
        response = ""
        for chunk in agent.process_message_stream(inputs["message"], conversation_id="evaluation"):
            if chunk.get('type') == 'message':
                response = chunk['text']
        return {"response": response}
    
    return target_function

def run_evaluation_pipeline(
    client: Client,
    agent: ConstructionAgent,
    dataset_name: str,
    experiment_prefix: str = "agent-evaluation",
    max_concurrency: int = 1,
    num_repetitions: int = 1
) -> Any:
    """Run the complete evaluation pipeline.
    
    Args:
        client: LangSmith client instance
        agent: ConstructionAgent instance to evaluate
        dataset_name: Name of the dataset to use
        experiment_prefix: Prefix for the experiment name
        max_concurrency: Maximum number of concurrent evaluations
        num_repetitions: Number of times to repeat each evaluation
        
    Returns:
        Experiment results
    """
    # Build or get dataset
    build_dataset(client, dataset_name)
    
    # Create target function and evaluator
    target_function = create_target_function(agent)
    
    # Run evaluation
    experiment_results = client.evaluate(
        target_function,
        data=dataset_name,
        evaluators=[evaluator_more_than_2_words],
        experiment_prefix=experiment_prefix,
        max_concurrency=max_concurrency,
        num_repetitions=num_repetitions
    )
    
    return experiment_results 