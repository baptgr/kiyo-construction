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

from kiyo_agents.construction_agent import ConstructionAgentFactory

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
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize agent factory with API key from environment
        factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
        agent = factory.create_agent()
        
        # Process message (synchronously in this case)
        response = async_to_sync(agent.process_message)(message, conversation_id)
        
        return JsonResponse(response)
    except Exception as e:
        # Log the actual error but return generic message
        print(f"API error: {str(e)}")
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
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Define a synchronous generator function for the StreamingHttpResponse
        def sync_event_stream():
            # SSE header for retry
            yield "retry: 1000\n\n"
            
            # Initialize agent
            factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
            agent = factory.create_agent()
            
            # Create and run the loop for async streaming
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Get the async stream generator
                stream_gen = agent.get_stream(message, conversation_id)
                
                # Consume the generator synchronously
                while True:
                    try:
                        # Get the next chunk from the stream
                        chunk = loop.run_until_complete(stream_gen.__anext__())
                        
                        # Format each chunk as an SSE event
                        if 'error' in chunk:
                            data = json.dumps({'error': chunk['error']})
                            yield f"event: error\ndata: {data}\n\n"
                            break
                        elif chunk.get('finished', False):
                            data = json.dumps({'finished': True})
                            yield f"event: done\ndata: {data}\n\n"
                            break
                        elif 'text' in chunk:
                            data = json.dumps({
                                'text': chunk['text'],
                                'finished': False
                            })
                            yield f"event: chunk\ndata: {data}\n\n"
                    
                    except StopAsyncIteration:
                        # End of stream
                        break
                    except Exception as e:
                        # Handle errors in stream processing
                        error_data = json.dumps({'error': str(e)})
                        yield f"event: error\ndata: {error_data}\n\n"
                        break
            
            except Exception as e:
                # Handle initialization errors
                error_data = json.dumps({'error': str(e)})
                yield f"event: error\ndata: {error_data}\n\n"
            finally:
                # Clean up the loop
                loop.close()
        
        # Return a properly configured SSE response with the sync generator
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
