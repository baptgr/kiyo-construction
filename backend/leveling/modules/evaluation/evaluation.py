import logging
from datetime import datetime
import os
import uuid
from dotenv import load_dotenv
from typing import Dict, Any, Callable
from langsmith import Client
from kiyo_agents.construction_agent import ConstructionAgent
from kiyo_agents.message_builder import build_agent_input_message
from kiyo_agents.pdf_processor import process_pdf_file
import os

from .evaluators.evaluators import EVALUATORS_FUNCTIONS
from .data_extraction import EXTRACTION_FUNCTIONS
from .file_processing import create_sheet_from_template

logger = logging.getLogger(__name__)

load_dotenv()
def create_target_function(google_access_token: str, run_id: str, dataset_name: str) -> Callable:
    """Create a target function that processes file inputs and returns agent responses."""

    def target_function(inputs: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Create Google Sheet from template
        template_path = inputs["template_path"]
        sheet_id = create_sheet_from_template(template_path, google_access_token, run_id)
        
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

        # 4. Initialize agent
        agent = ConstructionAgent(
            api_key=os.getenv('OPENAI_API_KEY'),
            google_access_token=google_access_token,
            spreadsheet_id=sheet_id
        )
        
        # 5. Process with agent
        # create unique conversation id
        conversation_id = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
        response = agent.process_message(message, conversation_id=conversation_id)

        # 6. Extract data from Google Sheet
        data = EXTRACTION_FUNCTIONS[dataset_name](sheet_id)
        
        return {
            "sheet_id": sheet_id,
            "response": response,
            "data": data
        }
    
    return target_function

def run_evaluation_pipeline(
    client: Client,
    dataset_name: str = "template-1",
    google_access_token: str = None,
    num_repetitions: int = 2
) -> Dict[str, Any]:
    """Run the full evaluation pipeline."""
    # Generate a unique run ID for this evaluation
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Get the dataset
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
    except Exception as e:
        raise ValueError(f"Dataset {dataset_name} not found. Please create it first using the create_evaluation_dataset command.") from e
    
    # Create target function
    target_function = create_target_function(
        google_access_token, run_id, dataset_name)
    
    # Run evaluation
    experiment_results = client.evaluate(
        target_function,
        data=dataset,
        evaluators=EVALUATORS_FUNCTIONS[dataset_name],
        experiment_prefix="agent-evaluation", 
        num_repetitions=num_repetitions
    )
    
    return experiment_results 