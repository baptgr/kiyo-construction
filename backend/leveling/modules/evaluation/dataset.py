from typing import Dict, Any
from langsmith import Client
import os
from django.conf import settings

def create_evaluation_dataset(
    client: Client,
    template_name: str = "template-1"
) -> Dict[str, Any]:
    """Create a dataset for evaluating the construction agent.
    
    Args:
        client: LangSmith client instance
        dataset_name: Name of the dataset to create
        
    Returns:
        The created dataset
    """
    try:
        # Try to read existing dataset
        dataset = client.read_dataset(dataset_name=template_name)
        print(f"Dataset {template_name} already exists")

    except Exception:
        # Create new dataset if it doesn't exist
        dataset = client.create_dataset(
            dataset_name=template_name,
            description="Dataset for evaluating construction agent with file inputs"
        )
        print(f"Created new dataset: {template_name}")
        
    # Add examples with file paths
    examples = [
        {
            "inputs": {
                "message": "Hello, how are you?",
                "template_path": os.path.join(settings.BASE_DIR, f"data/templates/{template_name}.xlsx"),
                "pdf_paths": [
                    os.path.join(settings.BASE_DIR, "data/pdfs/electrical_bid_3.pdf"),
                    os.path.join(settings.BASE_DIR, "data/pdfs/electrical_bid_4.pdf"),
                    os.path.join(settings.BASE_DIR, "data/pdfs/electrical_bid_5.pdf"),
                ]
            },
        }
    ]
    
    # Add all examples at once
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )
    print(f"Added {len(examples)} examples to dataset")
        
    return dataset 