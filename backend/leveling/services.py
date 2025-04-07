from typing import List, Dict, Any, Optional
from asgiref.sync import sync_to_async
from .models import Conversation, Message
import logging

logger = logging.getLogger(__name__)

class DatabaseMemoryStore:
    @sync_to_async
    def get_or_create_conversation(self, conversation_id: str, user_id: Optional[str] = None) -> Conversation:
        """Get or create a conversation by ID."""
        conversation, created = Conversation.objects.get_or_create(
            id=conversation_id,
            defaults={'user_id': user_id}
        )
        if created:
            logger.info(f"Created new conversation: {conversation_id}")
        return conversation

    @sync_to_async
    def add_message(self, conversation_id: str, role: str, content: str, 
                   item_type: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a message to the conversation."""
        conversation = Conversation.objects.get(id=conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            role=role,
            content=content,
            item_type=item_type,
            metadata=metadata or {}
        )
        # Update conversation timestamp
        conversation.save()  # This updates the updated_at field
        logger.info(f"Added message to conversation {conversation_id}: {role}")
        return message

    @sync_to_async
    def get_conversation_messages(self, conversation_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get the most recent messages from a conversation."""
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('-created_at')[:limit]
        
        # Convert to list of dicts in reverse chronological order
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "item_type": msg.item_type,
                "metadata": msg.metadata
            }
            for msg in reversed(messages)  # Reverse to get chronological order
        ]

    @sync_to_async
    def get_conversation_context(self, conversation_id: str, limit: int = 20) -> str:
        """Get conversation context formatted for the agent."""
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('-created_at')[:limit]
        
        if not messages:
            return ""
        
        # Format messages as context
        context_messages = [
            f"{msg.role}: {msg.content}"
            for msg in reversed(messages)  # Reverse to get chronological order
        ]
        
        return "Previous conversation:\n" + "\n".join(context_messages) + "\n---\n"

    @sync_to_async
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages."""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            conversation.delete()
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        except Conversation.DoesNotExist:
            logger.warning(f"Attempted to delete non-existent conversation: {conversation_id}")
            return False 