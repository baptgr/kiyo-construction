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
from asgiref.sync import async_to_sync
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
        data = json.loads(request.body)
        message = data.get('message', '')
        conversation_id = data.get('conversation_id', 'default')
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
        agent = factory.create_agent()
        
        response = async_to_sync(agent.process_message)(message, conversation_id)
        
        return JsonResponse(response)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        def generate_stream():
            yield "retry: 1000\n\n"
            
            try:
                factory = ConstructionAgentFactory(api_key=os.environ.get('OPENAI_API_KEY'))
                agent = factory.create_agent()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(agent.process_message(message, conversation_id))
                finally:
                    loop.close()
                
                full_text = response.get('text', '')
                words = full_text.split(' ')
                
                for i, word in enumerate(words):
                    if not word:
                        continue
                        
                    word_chunk = word + (' ' if i < len(words) - 1 else '')
                    data = json.dumps({"text": word_chunk, "finished": False})
                    yield f"event: chunk\ndata: {data}\n\n"
                    
                    time.sleep(0.05)
                
                yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
                
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
        
        response = StreamingHttpResponse(
            generate_stream(),
            content_type='text/event-stream'
        )
        
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 