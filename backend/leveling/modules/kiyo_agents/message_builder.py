from typing import List, Dict, Any, Optional

def build_agent_input_message(
    message: Optional[str],
    processed_pdfs: List[Dict[str, str]],
    spreadsheet_id: Optional[str]
) -> str:
    """Build the final input message for the agent.
    
    Args:
        message: The user's message
        processed_pdfs: List of processed PDF contents
        spreadsheet_id: ID of the Google Sheet to use
        
    Returns:
        The combined input message
    """
    final_input_message = ""
    pdf_combined_content = ""

    if processed_pdfs:
        for pdf_data in processed_pdfs:
            pdf_combined_content += f"--- PDF Content Start: {pdf_data['filename']} ---\n{pdf_data['content']}\n--- PDF Content End: {pdf_data['filename']} ---\n\n"
        
        final_input_message += pdf_combined_content

    if message:
        final_input_message += f"User Message: {message}"
    elif not pdf_combined_content:
        raise ValueError('Message or PDF attachment is required')

    if spreadsheet_id:
        if message and not message.lower().startswith("use spreadsheet"): 
            enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {final_input_message}"
        else:
            enhanced_message = final_input_message
    else:
        enhanced_message = final_input_message
    
    return enhanced_message 