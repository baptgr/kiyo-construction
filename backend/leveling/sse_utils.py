from typing import AsyncGenerator, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

async def convert_agent_stream_to_sse(
    agent_stream: AsyncGenerator[Dict[str, Any], None]
) -> AsyncGenerator[str, None]:
    """
    Convert an agent's stream of responses to Server-Sent Events format.
    
    Args:
        agent_stream: Async generator yielding agent response chunks
        
    Yields:
        SSE-formatted strings
    """
    try:
        #logger.info("Starting SSE conversion")
        # SSE header
        yield "retry: 1000\n\n"
        #logger.info("Sent SSE header")
        
        chunk_count = 0
        async for chunk in agent_stream:
            chunk_count += 1
            #logger.info(f"Processing chunk {chunk_count}")
            
            if chunk["type"] == "message":
                sse_event = f"event: chunk\ndata: {json.dumps({'text': chunk['text'], 'finished': False})}\n\n"
                #logger.info(f"Sending message chunk: {chunk['text'][:50]}...")
                yield sse_event
            elif chunk["type"] == "tool_call":
                sse_event = f"event: tool_call\ndata: {json.dumps(chunk['tool_calls'])}\n\n"
                #logger.info(f"Sending tool call chunk: {json.dumps(chunk['tool_calls'])}")
                yield sse_event
                
        #logger.info(f"Stream completed. Processed {chunk_count} chunks.")
        # Send final done event
        yield f"event: done\ndata: {json.dumps({'finished': True})}\n\n"
            
    except Exception as e:
        logger.error(f"Error in SSE conversion: {str(e)}", exc_info=True)
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

def create_sse_response(stream_generator: AsyncGenerator[str, None]):
    """
    Create a StreamingHttpResponse with proper SSE headers.
    
    Args:
        stream_generator: Async generator yielding SSE-formatted strings
        
    Returns:
        StreamingHttpResponse configured for SSE
    """
    from django.http import StreamingHttpResponse
    
    #logger.info("Creating SSE response")
    response = StreamingHttpResponse(
        stream_generator,
        content_type='text/event-stream'
    )
    
    # Required headers for SSE
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    
    #logger.info("SSE response created with headers")
    return response 