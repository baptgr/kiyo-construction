from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import os
import time
import tempfile
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
import logging
import traceback
from typing import Tuple, Optional, Dict, Any, IO, List

from kiyo_agents.construction_agent import ConstructionAgent
from kiyo_agents.pdf_processor import process_pdf_upload

# Configure more detailed logging
logger = logging.getLogger(__name__)

# Helper Functions for chat_stream

def _parse_request_data(request) -> Tuple[Optional[str], Optional[str], Optional[str], str, List[IO]]:
    """Parses request data from JSON or FormData."""
    message = None
    google_access_token = None
    spreadsheet_id = None
    conversation_id = f'default_{time.time()}' # Default conversation ID
    pdf_files = []

    if request.content_type == 'application/json':
        logger.info("Processing JSON request")
        data = json.loads(request.body)
        message = data.get('message')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        conversation_id = data.get('conversation_id', conversation_id)
        pdf_files = request.FILES.getlist('pdf_files')
    elif request.content_type.startswith('multipart/form-data'):
        logger.info("Processing FormData request")
        message = request.POST.get('message')
        google_access_token = request.POST.get('google_access_token')
        spreadsheet_id = request.POST.get('spreadsheet_id')
        conversation_id = request.POST.get('conversation_id', conversation_id)
        pdf_files = request.FILES.getlist('pdf_files')
    else:
        logger.error(f"Unsupported content type: {request.content_type}")
        raise ValueError('Unsupported content type')

    return message, google_access_token, spreadsheet_id, conversation_id, pdf_files


def _build_agent_input_message(message: Optional[str], processed_pdfs: List[Dict[str, str]], spreadsheet_id: Optional[str]) -> str:
    """Builds the final input message for the agent, combining text from multiple PDFs."""
    final_input_message = ""
    pdf_combined_content = ""

    if processed_pdfs:
        for pdf_data in processed_pdfs:
            pdf_combined_content += f"--- PDF Content Start: {pdf_data['filename']} ---\n{pdf_data['content']}\n--- PDF Content End: {pdf_data['filename']} ---\n\n"
        
        final_input_message += pdf_combined_content

    if message:
         final_input_message += f"User Message: {message}"
    elif not pdf_combined_content:
         logger.warning("Received request with no text message and no valid/processed PDF attachments.")
         raise ValueError('Message or PDF attachment is required')

    if spreadsheet_id:
        if message and not message.lower().startswith("use spreadsheet"): 
            enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {final_input_message}"
            logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
        else:
            enhanced_message = final_input_message
    else:
        enhanced_message = final_input_message
    
    logger.info(f"Final combined message for agent (start): {enhanced_message[:100]}...")
    return enhanced_message


def _generate_sse_stream(agent_input: str, conv_id: str, g_token: Optional[str], ss_id: Optional[str]):
    """Generator function for Server-Sent Events stream."""
    try:
        logger.info(f"Creating agent instance for stream {conv_id}")
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set.")
            raise ValueError("API key not configured.")
            
        agent = ConstructionAgent(
            api_key=api_key,
            google_access_token=g_token,
            spreadsheet_id=ss_id
        )
        
        #logger.info(f"Starting message processing stream for {conv_id}")
        
        for chunk in agent.process_message_stream(
            agent_input, 
            conversation_id=conv_id,
            spreadsheet_id=ss_id
        ):
            if chunk["type"] == "message":
                yield f"event: chunk\ndata: {json.dumps({'text': chunk['text'], 'finished': False})}\n\n"
            elif chunk["type"] == "tool_call":
                yield f"event: tool_call\ndata: {json.dumps(chunk['tool_calls'])}\n\n"
        
        yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
            
    except Exception as e:
        logger.error(f"Error in stream generation for {conv_id}: {str(e)}", exc_info=True)
        error_payload = json.dumps({'error': 'An error occurred during processing.'})
        yield f"event: error\ndata: {error_payload}\n\n"


# API Views

@api_view(['GET'])
@permission_classes([AllowAny])
def hello_world(request):
    """
    Basic hello world endpoint
    """
    return Response({
        'message': 'Hello World! Welcome to the Kiyo Construction API'
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_stream(request):
    """
    Stream the agent's response using Server-Sent Events (SSE).
    Handles both JSON and FormData requests (for PDF uploads).
    Refactored for clarity and multiple PDF support.
    """
    try:
        # 1. Parse Request Data (receives pdf_files list)
        try:
            message, google_access_token, spreadsheet_id, conversation_id, pdf_files = _parse_request_data(request)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=415 if 'content type' in str(e) else 400)

        logger.info(f"Processing chat stream request for conversation {conversation_id}. Message: {message[:50] if message else 'N/A'}. Files received: {len(pdf_files)}")

        # 2. Process potentially multiple PDFs
        processed_pdfs = []
        if pdf_files:
            #logger.info(f"Processing {len(pdf_files)} uploaded PDF file(s)...")
            for pdf_file in pdf_files:
                try:
                    pdf_text_content = process_pdf_upload(pdf_file)
                    if pdf_text_content:
                         processed_pdfs.append({'filename': pdf_file.name, 'content': pdf_text_content})
                         logger.info(f"Successfully processed: {pdf_file.name}")
                    else:
                         logger.warning(f"Processing PDF '{pdf_file.name}' resulted in empty content.")
                except Exception as pdf_exc:
                     logger.error(f"Error processing PDF file '{pdf_file.name}': {pdf_exc}", exc_info=True)

        # 3. Build Agent Input Message using processed PDF data
        try:
            agent_input_message = _build_agent_input_message(message, processed_pdfs, spreadsheet_id)
        except ValueError as e:
             return JsonResponse({'error': str(e)}, status=400)

        # 4. Generate and Return SSE Stream
        #logger.info("Creating SSE response")
        response = StreamingHttpResponse(
            _generate_sse_stream(agent_input_message, conversation_id, google_access_token, spreadsheet_id),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
        
    except Exception as e:
        logger.error(f"Fatal error in chat_stream: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
