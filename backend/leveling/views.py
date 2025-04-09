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
from typing import Tuple, Optional, Dict, Any, IO

from kiyo_agents.construction_agent import ConstructionAgent
from kiyo_agents.pdf_processor import process_pdf_upload

# Configure more detailed logging
logger = logging.getLogger(__name__)

# Helper Functions for chat_stream

def _parse_request_data(request) -> Tuple[Optional[str], Optional[str], Optional[str], str, Optional[IO]]:
    """Parses request data from JSON or FormData."""
    message = None
    google_access_token = None
    spreadsheet_id = None
    conversation_id = f'default_{time.time()}' # Default conversation ID
    pdf_file = None

    if request.content_type == 'application/json':
        logger.info("Processing JSON request")
        data = json.loads(request.body)
        message = data.get('message')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        conversation_id = data.get('conversation_id', conversation_id)
    elif request.content_type.startswith('multipart/form-data'):
        logger.info("Processing FormData request")
        message = request.POST.get('message')
        google_access_token = request.POST.get('google_access_token')
        spreadsheet_id = request.POST.get('spreadsheet_id')
        conversation_id = request.POST.get('conversation_id', conversation_id)
        pdf_file = request.FILES.get('pdf_file')
    else:
        logger.error(f"Unsupported content type: {request.content_type}")
        raise ValueError('Unsupported content type')

    return message, google_access_token, spreadsheet_id, conversation_id, pdf_file


def _build_agent_input_message(message: Optional[str], pdf_text_content: str, spreadsheet_id: Optional[str]) -> str:
    """Builds the final input message for the agent."""
    final_input_message = ""
    
    if pdf_text_content:
        final_input_message += f"--- Start Attached PDF Content ---\n{pdf_text_content}\n--- End Attached PDF Content ---\n\n"

    # Append user message only if it's not empty
    if message:
         final_input_message += f"User Message: {message}"
    elif not pdf_text_content:
         # Handle case where user sends neither text nor file
         logger.warning("Received request with no text message and no (or failed) PDF attachment.")
         raise ValueError('Message or PDF attachment is required')

    # Handle spreadsheet context injection
    if spreadsheet_id:
        # Avoid redundant phrasing if user already mentions spreadsheet or if PDF is the main content
        if message and not message.lower().startswith("use spreadsheet"): 
            enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {final_input_message}"
            logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
        else:
            enhanced_message = final_input_message # Use combined message as is
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
            spreadsheet_id=ss_id # Pass spreadsheet_id here too
        )
        
        logger.info(f"Starting message processing stream for {conv_id}")
        
        for chunk in agent.process_message_stream(
            agent_input, 
            conversation_id=conv_id,
            spreadsheet_id=ss_id # Pass spreadsheet_id to processing method
        ):
            if chunk["type"] == "message":
                yield f"event: chunk\ndata: {json.dumps({'text': chunk['text'], 'finished': False})}\n\n"
            elif chunk["type"] == "tool_call":
                yield f"event: tool_call\ndata: {json.dumps(chunk['tool_calls'])}\n\n"
        
        yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
            
    except Exception as e:
        logger.error(f"Error in stream generation for {conv_id}: {str(e)}", exc_info=True)
        # Send error event to client
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
    Refactored for clarity.
    """
    try:
        # 1. Parse Request Data
        try:
            message, google_access_token, spreadsheet_id, conversation_id, pdf_file = _parse_request_data(request)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=415 if 'content type' in str(e) else 400)

        logger.info(f"Processing chat stream request for conversation {conversation_id}. Message: {message[:50] if message else 'N/A'}...")

        # 2. Process PDF if uploaded
        pdf_text_content = process_pdf_upload(pdf_file) if pdf_file else ""

        # 3. Build Agent Input Message
        try:
            agent_input_message = _build_agent_input_message(message, pdf_text_content, spreadsheet_id)
        except ValueError as e:
             return JsonResponse({'error': str(e)}, status=400)

        # 4. Generate and Return SSE Stream
        logger.info("Creating SSE response")
        response = StreamingHttpResponse(
            _generate_sse_stream(agent_input_message, conversation_id, google_access_token, spreadsheet_id),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no' # Often needed for Nginx etc.
        return response
        
    except Exception as e:
        # Catch-all for unexpected errors during setup/processing
        logger.error(f"Fatal error in chat_stream: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
