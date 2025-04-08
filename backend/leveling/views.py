from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import asyncio
import os
import time
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
import logging
import traceback
from typing import AsyncGenerator

from kiyo_agents.construction_agent import ConstructionAgent
from .sse_utils import convert_agent_stream_to_sse, create_sse_response

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
@csrf_exempt
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
            google_access_token=google_access_token
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
        response = async_to_sync(agent.process_message)(
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
@csrf_exempt
def chat_stream(request):
    """
    Stream the agent's response using Server-Sent Events (SSE)
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        conversation_id = data.get('conversation_id', f'default_{time.time()}')
        
        logger.info(f"Processing chat stream request for conversation {conversation_id}. Message: {message[:50]}...")
        
        if not message:
            logger.warning("Empty message received")
            return JsonResponse({'error': 'Message is required'}, status=400)

        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                logger.info("Creating agent instance")
                # Create a new agent instance
                api_key = os.environ.get('OPENAI_API_KEY')
                agent = ConstructionAgent(
                    api_key=api_key,
                    google_access_token=google_access_token
                )
                
                # Store spreadsheet ID in the conversation context if provided
                if spreadsheet_id:
                    if not message.lower().startswith("use spreadsheet"):
                        enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {message}"
                        logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
                    else:
                        enhanced_message = message
                else:
                    enhanced_message = message
                
                logger.info(f"Starting message processing with enhanced message: {enhanced_message[:50]}...")
                
                # Get the agent's stream with conversation ID
                agent_stream = agent.process_message_stream(
                    enhanced_message, 
                    conversation_id=conversation_id,
                    spreadsheet_id=spreadsheet_id
                )
                
                logger.info("Starting SSE conversion")
                # Convert to SSE format
                async for sse_event in convert_agent_stream_to_sse(agent_stream):
                    yield sse_event
                    
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                
        logger.info("Creating SSE response")
        # Create and return the SSE response
        response = create_sse_response(generate_stream())
        response['X-Accel-Buffering'] = 'no'
        return response
        
    except Exception as e:
        logger.error(f"Error in chat_stream: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
