import json
import asyncio
from typing import AsyncIterator, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SSESerializer:
    """Server-Sent Events serializer for streaming responses."""
    
    @staticmethod
    def serialize_sse(data: Dict[str, Any], event: Optional[str] = None) -> str:
        """Serialize data to SSE format.
        
        Args:
            data: The data to serialize
            event: Optional event name
            
        Returns:
            String in SSE format
        """
        message = []
        if event is not None:
            message.append(f"event: {event}")
        
        # Ensure data is serialized to JSON
        serialized_data = json.dumps(data)
        
        # Split the data by newlines and prefix each line with "data: "
        for line in serialized_data.split("\n"):
            message.append(f"data: {line}")
            
        # End with a double newline
        message.append("\n")
        return "\n".join(message)
    
    @staticmethod
    async def stream_sse_response(data_iterator: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[str]:
        """Convert an async iterator of data to an async iterator of SSE-formatted strings.
        
        Args:
            data_iterator: Async iterator of data dictionaries
            
        Yields:
            SSE-formatted strings
        """
        try:
            async for data in data_iterator:
                # If this is a chunk, set the event type to "chunk"
                event = "chunk" if not data.get("finished", False) else "message"
                yield SSESerializer.serialize_sse(data, event=event)
                
                # If this is the final chunk, send a completion event
                if data.get("finished", False):
                    yield SSESerializer.serialize_sse({"type": "done"}, event="done")
        except Exception as e:
            logger.error(f"Error in SSE streaming: {e}")
            # Send an error event
            yield SSESerializer.serialize_sse(
                {"error": str(e), "type": "error"}, 
                event="error"
            ) 