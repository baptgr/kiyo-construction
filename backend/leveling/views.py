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
        conversation_id = data.get('conversation_id', 'default')
        google_access_token = data.get('google_access_token')
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize agent factory with API key from environment
        factory = ConstructionAgentFactory(
            api_key=os.environ.get('OPENAI_API_KEY'),
            google_access_token=google_access_token
        )
        agent = factory.create_agent()
        
        # Process message (synchronously in this case)
        response = async_to_sync(agent.process_message)(message, conversation_id)
        
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
    Process a chat message and stream the response using Server-Sent Events (SSE).
    """
    try:
        # Get message from request
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        google_access_token = data.get('google_access_token')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Create a function that runs the entire streaming process in a single context
        def sync_event_stream():
            # SSE header for retry
            yield "retry: 1000\n\n"
            
            # Create a single event loop that will be used for the entire streaming process
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Initialize agent with Google access token
                factory = ConstructionAgentFactory(
                    api_key=os.environ.get('OPENAI_API_KEY'),
                    google_access_token=google_access_token
                )
                agent = factory.create_agent()
                
                # Create a single async function that handles the entire streaming process
                async def process_stream():
                    try:
                        # Use the agent's streaming method directly (not iterating over it yet)
                        stream = agent.get_stream(message, conversation_id)
                        
                        # Process each chunk in a single async context
                        async for chunk in stream:
                            if 'error' in chunk:
                                yield f"event: error\ndata: {json.dumps({'error': chunk['error']})}\n\n"
                                return
                            elif chunk.get('finished', False):
                                yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
                                return
                            elif 'text' in chunk:
                                yield f"event: chunk\ndata: {json.dumps({'text': chunk['text'], 'finished': False})}\n\n"
                    except Exception as e:
                        print(f"Error in async stream processing: {e}")
                        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                
                # Create a generator that yields chunks from the async process
                async def async_generator():
                    async for item in process_stream():
                        yield item
                
                # Run the entire streaming process and yield chunks synchronously
                generator = async_generator()
                while True:
                    try:
                        # Get the next chunk from the generator in the same context
                        chunk = loop.run_until_complete(generator.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
                    except Exception as e:
                        print(f"Error in sync wrapper: {e}")
                        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
                        break
            
            finally:
                # Clean up the loop
                loop.close()
        
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
        return JsonResponse({'error': str(e)}, status=500)
