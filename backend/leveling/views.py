from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json
import asyncio
import os
from django.http import StreamingHttpResponse, JsonResponse
from asgiref.sync import async_to_sync, sync_to_async
from django.views.decorators.csrf import csrf_exempt

from kiyo_agents.construction_agent import ConstructionAgentFactory
from kiyo_agents.streaming import SSESerializer

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
    Process a chat message and stream the response using SSE.
    """
    try:
        # Get message from request
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        # Define a proper sync iterator that wraps the async logic
        def iterator():
            # Get our agent
            factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
            agent = factory.create_agent()
            
            # Create an event loop for async operations
            loop = asyncio.new_event_loop()
            
            async def process_stream():
                try:
                    # Get the message stream
                    response_iterator = agent.process_message_stream(message, conversation_id)
                    
                    # Process it through our SSE formatter
                    async for chunk in SSESerializer.stream_sse_response(response_iterator):
                        yield chunk
                except Exception as e:
                    # Handle errors
                    error_message = SSESerializer.serialize_sse(
                        {"error": str(e), "type": "error"}, 
                        event="error"
                    )
                    yield error_message
            
            # Run the async generator in the loop and yield results
            agen = process_stream()
            try:
                while True:
                    try:
                        chunk = loop.run_until_complete(agen.__anext__())
                        yield chunk
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()
        
        # Create the streaming response with our sync iterator
        response = StreamingHttpResponse(
            streaming_content=iterator(),
            content_type='text/event-stream',
        )
        
        # Set headers for SSE (remove the Connection header which is not allowed)
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # For Nginx
        
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
