from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import asyncio
import os
import time
from django.http import StreamingHttpResponse, JsonResponse
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
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def chat_stream(request):
    """
    Very simple streaming approach that just streams the agent's response with words
    """
    try:
        # Get message from request
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Define generator function for the streaming response
        def generate_stream():
            # Send SSE format retry directive
            yield "retry: 1000\n\n"
            
            try:
                # Initialize the agent
                factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
                agent = factory.create_agent()
                
                # Get the full response first (no streaming from OpenAI)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(agent.process_message(message, conversation_id))
                finally:
                    loop.close()
                
                # Get the text response
                full_text = response.get('text', '')
                
                # Split the text by words for a more natural streaming
                words = full_text.split(' ')
                
                # Stream the words one at a time with spaces
                for i, word in enumerate(words):
                    if not word:
                        continue
                        
                    word_chunk = word + (' ' if i < len(words) - 1 else '')
                    data = json.dumps({"text": word_chunk, "finished": False})
                    yield f"event: chunk\ndata: {data}\n\n"
                    
                    # Small delay to make the streaming visible
                    time.sleep(0.05)
                
                # Send completion event
                yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
                
            except Exception as e:
                # Send error event
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
        # Create the streaming response
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        
        # Set required headers for SSE
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 