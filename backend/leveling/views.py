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
from asgiref.sync import async_to_sync, sync_to_async
from django.views.decorators.csrf import csrf_exempt
import logging
import traceback

from kiyo_agents.construction_agent import ConstructionAgentFactory

# Configure more detailed logging
logger = logging.getLogger(__name__)

# Module-level agent cache to maintain agent instances between requests
# Key: (api_key, google_access_token), Value: agent instance
_AGENT_CACHE = {}

def _get_cached_agent(api_key, google_access_token=None):
    """Get or create an agent instance from the cache."""
    # Create a key from the API key and access token
    cache_key = (api_key, google_access_token)
    
    # Check if we already have an agent for this key
    if cache_key not in _AGENT_CACHE:
        logger.info(f"Creating new agent instance (cache miss)")
        factory = ConstructionAgentFactory(
            api_key=api_key,
            google_access_token=google_access_token
        )
        agent = factory.create_agent()
        _AGENT_CACHE[cache_key] = agent
        logger.info(f"New agent created, conversation count: {len(agent.conversations)}")
    else:
        agent = _AGENT_CACHE[cache_key]
        logger.info(f"Reusing cached agent instance (cache hit), conversation count: {len(agent.conversations)}")
        
        # Debug: List conversations
        for conv_id, msgs in agent.conversations.items():
            logger.info(f"Conversation {conv_id}: {len(msgs)} messages")
    
    return _AGENT_CACHE[cache_key]

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
        conversation_id = data.get('conversation_id', 'default')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        
        logger.info(f"Processing chat for conversation_id: {conversation_id}")
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cached agent instance
        api_key = os.environ.get('OPENAI_API_KEY')
        agent = _get_cached_agent(api_key, google_access_token)
        
        # Log conversation state before processing
        conv_exists = conversation_id in agent.conversations
        conv_messages = len(agent.conversations.get(conversation_id, []))
        logger.info(f"Before processing - Conversation exists: {conv_exists}, messages: {conv_messages}")
        
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
        
        # Process message (synchronously in this case)
        response = async_to_sync(agent.process_message)(enhanced_message, conversation_id)
        
        # Log conversation state after processing
        conv_exists = conversation_id in agent.conversations
        conv_messages = len(agent.conversations.get(conversation_id, []))
        logger.info(f"After processing - Conversation exists: {conv_exists}, messages: {conv_messages}")
        
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
    Stream the agent's response word by word using SSE
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        google_access_token = data.get('google_access_token')
        spreadsheet_id = data.get('spreadsheet_id')
        
        logger.info(f"Processing chat_stream for conversation_id: {conversation_id}")
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Create a function that runs the entire streaming process
        def sync_event_stream():
            # SSE header for retry
            yield "retry: 1000\n\n"
            
            try:
                # Get cached agent instance
                api_key = os.environ.get('OPENAI_API_KEY')
                agent = _get_cached_agent(api_key, google_access_token)
                
                # Log conversation state before processing
                conv_exists = conversation_id in agent.conversations
                conv_messages = len(agent.conversations.get(conversation_id, []))
                logger.info(f"Before streaming - Conversation exists: {conv_exists}, messages: {conv_messages}")
                
                # Store spreadsheet ID in the conversation context if provided
                if spreadsheet_id:
                    # Update conversation context by enhancing the message
                    if not message.lower().startswith("use spreadsheet"):
                        enhanced_message = f"Use spreadsheet with ID {spreadsheet_id} for this task. {message}"
                        logger.info(f"Enhanced message with spreadsheet ID: {spreadsheet_id}")
                    else:
                        enhanced_message = message
                else:
                    enhanced_message = message
                
                # Create a single event loop for the entire streaming process
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Get the stream from the agent
                    logger.info(f"Getting stream from agent for message: {enhanced_message[:30]}...")
                    stream = agent.get_stream(enhanced_message, conversation_id)
                    
                    # Process each chunk from the stream
                    async def process_stream():
                        try:
                            logger.info("Starting to process streaming response")
                            message_count = 0
                            async for chunk in stream:
                                message_count += 1
                                if message_count % 10 == 0:
                                    logger.info(f"Processed {message_count} message chunks so far")
                                    
                                if 'error' in chunk:
                                    logger.error(f"Error in stream response: {chunk['error']}")
                                    yield f"event: error\ndata: {json.dumps({'error': chunk['error']})}\n\n"
                                elif chunk.get('finished', False):
                                    logger.info("Stream finished")
                                    yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
                                elif 'text' in chunk:
                                    # For text chunks, just pass them through
                                    yield f"event: chunk\ndata: {json.dumps({'text': chunk['text'], 'finished': False})}\n\n"
                            
                            # Log conversation state after streaming
                            conv_exists = conversation_id in agent.conversations
                            conv_messages = len(agent.conversations.get(conversation_id, []))
                            logger.info(f"After streaming - Conversation exists: {conv_exists}, messages: {conv_messages}")
                            
                        except Exception as e:
                            logger.error(f"Error in async stream processing: {e}", exc_info=True)
                            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                    
                    # Create a generator that yields chunks from the async process
                    async def async_generator():
                        async for item in process_stream():
                            yield item
                    
                    # Run the generator and yield each chunk
                    generator = async_generator()
                    while True:
                        try:
                            chunk = loop.run_until_complete(generator.__anext__())
                            yield chunk
                        except StopAsyncIteration:
                            logger.info("Stream generation complete")
                            break
                finally:
                    # Clean up the loop
                    loop.close()
                    
            except Exception as e:
                logger.error(f"Error in streaming: {str(e)}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
        # Return a properly configured SSE response
        response = StreamingHttpResponse(
            sync_event_stream(),
            content_type='text/event-stream'
        )
        
        # Required headers for SSE
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # For Nginx
        
        return response
    except Exception as e:
        logger.error(f"Error in chat_stream: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
