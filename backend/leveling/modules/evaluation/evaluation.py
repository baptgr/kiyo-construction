import logging

from typing import Dict, Any, Callable
from langsmith import Client
from kiyo_agents.construction_agent import ConstructionAgent
from kiyo_agents.message_builder import build_agent_input_message
from kiyo_agents.pdf_processor import process_pdf_file
import os

from .evaluators import evaluator_more_than_2_words
from .file_processing import create_sheet_from_template

logger = logging.getLogger(__name__)


def create_target_function(agent: ConstructionAgent) -> Callable:
    """Create a target function that processes file inputs and returns agent responses."""
    def target_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Create Google Sheet from template
        template_path = inputs["template_path"]
        sheet_id = create_sheet_from_template(template_path)
        
        # 2. Process PDFs
        pdf_contents = []
        for pdf_path in inputs["pdf_paths"]:
            content = process_pdf_file(pdf_path)
            # Create a dictionary with filename and content
            pdf_contents.append({
                "filename": os.path.basename(pdf_path),
                "content": content
            })
        
        # 3. Build combined message
        message = build_agent_input_message(
            message=inputs["message"],
            processed_pdfs=pdf_contents,
            spreadsheet_id=sheet_id
        )
        
        # 4. Process with agent
        response = agent.process_message(message, conversation_id="simulation")
        
        return {
            "sheet_id": sheet_id,
            "response": response
        }
    
    return target_function

def run_evaluation_pipeline(
    client: Client,
    agent: ConstructionAgent,
    dataset_name: str = "sample-dataset"
) -> Dict[str, Any]:
    """Run the full evaluation pipeline."""
    # Get the dataset
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception as e:
        raise ValueError(f"Dataset {dataset_name} not found. Please create it first using the create_evaluation_dataset command.") from e
    
    # Create target function
    target_function = create_target_function(agent)
    
    # Run evaluation
    experiment_results = client.evaluate(
        target_function,
        data=dataset,
        evaluators=[evaluator_more_than_2_words],
        experiment_prefix="agent-evaluation"
    )
    
    return experiment_results 