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

# Langchain PDF Loader
from langchain_community.document_loaders import PyPDFLoader

from kiyo_agents.construction_agent import ConstructionAgent

# Configure more detailed logging
logger = logging.getLogger(__name__)

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
def chat(request):
    """
    Process a chat message and return a response.
    """
    try:
        # Get message from request
        data = json.loads(request.body)
        message = data.get('message', '')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        conversation_id = data.get('conversation_id', f'default_{time.time()}')
        
        logger.info(f"Processing chat request for conversation {conversation_id}")
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new agent instance
        api_key = os.environ.get('OPENAI_API_KEY')
        agent = ConstructionAgent(
            api_key=api_key,
            google_access_token=google_access_token, 
            spreadsheet_id=spreadsheet_id
        )
        
        # Store spreadsheet ID in the conversation context if provided
        if spreadsheet_id:
            # Update conversation context
            enhanced_message = message
            if not message.lower().startswith("use spreadsheet"):
                # Only inject if the user isn't explicitly mentioning a spreadsheet
                enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {message}"
                logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
        else:
            enhanced_message = message
        
        # Process message with conversation ID
        response = agent.process_message(
            enhanced_message, 
            conversation_id=conversation_id,
            spreadsheet_id=spreadsheet_id
        )
        
        # Add conversation ID to response
        response['conversation_id'] = conversation_id
        
        return JsonResponse(response)
    except Exception as e:
        # Log the actual error but return generic message
        logger.error(f"API error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Error, something went wrong'}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_stream(request):
    """
    Stream the agent's response using Server-Sent Events (SSE).
    Handles both JSON and FormData requests (for PDF uploads).
    """
    message = ''
    google_access_token = None
    spreadsheet_id = None
    conversation_id = f'default_{time.time()}' # Default conversation ID
    pdf_file = None
    pdf_text_content = ''

    try:
        # Determine content type and parse accordingly
        if request.content_type == 'application/json':
            logger.info("Processing JSON request")
            data = json.loads(request.body)
            message = data.get('message', '')
            google_access_token = data.get('google_access_token')
            spreadsheet_id = data.get('spreadsheet_id')
            conversation_id = data.get('conversation_id', conversation_id)
        elif request.content_type.startswith('multipart/form-data'):
            logger.info("Processing FormData request")
            message = request.POST.get('message', '')
            google_access_token = request.POST.get('google_access_token')
            spreadsheet_id = request.POST.get('spreadsheet_id')
            conversation_id = request.POST.get('conversation_id', conversation_id)
            pdf_file = request.FILES.get('pdf_file')
        else:
            logger.error(f"Unsupported content type: {request.content_type}")
            return JsonResponse({'error': 'Unsupported content type'}, status=415)

        logger.info(f"Processing chat stream request for conversation {conversation_id}. Message: {message[:50]}...")

        # Process PDF if uploaded
        if pdf_file:
            logger.info(f"Processing uploaded PDF: {pdf_file.name}")
            temp_pdf_path = None
            try:
                # Save PDF to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                    temp_pdf_path = temp_pdf.name
                    for chunk in pdf_file.chunks():
                        temp_pdf.write(chunk)
                
                # Use PyPDFLoader to extract text
                loader = PyPDFLoader(temp_pdf_path)
                pages = loader.load() # or load_and_split()
                pdf_text_content = "\n\n".join([page.page_content for page in pages])
                logger.info(f"Extracted {len(pdf_text_content)} characters from PDF.")

            except Exception as pdf_err:
                logger.error(f"Error processing PDF {pdf_file.name}: {pdf_err}", exc_info=True)
                # Decide how to handle PDF error: Ignore, notify user, etc.
                # For now, we'll proceed without PDF content but log the error.
                pdf_text_content = "[Error processing attached PDF]"
            finally:
                # Ensure temporary file is deleted
                if temp_pdf_path and os.path.exists(temp_pdf_path):
                    try:
                        os.remove(temp_pdf_path)
                        logger.info(f"Deleted temporary PDF file: {temp_pdf_path}")
                    except OSError as del_err:
                        logger.error(f"Error deleting temporary PDF file {temp_pdf_path}: {del_err}")

        # Combine PDF content and user message
        final_input_message = ""
        if pdf_text_content:
            final_input_message += f"--- Start Attached PDF Content ---\n{pdf_text_content}\n--- End Attached PDF Content ---\n\n"
        
        # Append user message only if it's not empty
        if message:
             final_input_message += f"User Message: {message}"
        elif not pdf_text_content:
             # Handle case where user sends neither text nor file
             logger.warning("Received request with no text message and no (or failed) PDF attachment.")
             return JsonResponse({'error': 'Message or PDF attachment is required'}, status=400)

        # Handle spreadsheet context injection (if needed)
        if spreadsheet_id:
            # Avoid redundant phrasing if user already mentions spreadsheet or if PDF is the main content
            if not message.lower().startswith("use spreadsheet") and message: # Only enhance if there's a user message not about spreadsheets
                enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {final_input_message}"
                logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
            else:
                enhanced_message = final_input_message # Use combined message as is
        else:
            enhanced_message = final_input_message
            
        logger.info(f"Final combined message for agent (start): {enhanced_message[:100]}...")

        # Define the generator function, passing necessary context
        def generate_stream(agent_input, conv_id, g_token, ss_id):
            try:
                logger.info(f"Creating agent instance for stream {conv_id}")
                api_key = os.environ.get('OPENAI_API_KEY')
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
        
        logger.info("Creating SSE response")
        response = StreamingHttpResponse(
            generate_stream(enhanced_message, conversation_id, google_access_token, spreadsheet_id),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no' # Often needed for Nginx etc.
        return response
        
    except Exception as e:
        # Catch-all for errors during initial request parsing/setup
        logger.error(f"Fatal error in chat_stream setup: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
