from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Union, Any, Optional


class AgentInterface(ABC):
    """Abstract interface for agent interactions, allowing for decoupling from specific implementations."""
    
    @abstractmethod
    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a message and return a complete response."""
        pass
    
    @abstractmethod
    async def process_message_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Process a message and yield chunks of the response as they're generated."""
        pass
    
    @abstractmethod
    def get_stream(self, message: str, conversation_id: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """
        Get a streaming response from the agent.
        
        Returns an async iterator of response chunks.
        """
        pass


class AgentFactory(ABC):
    """Factory for creating agent instances."""
    
    @abstractmethod
    def create_agent(self, agent_type: str) -> AgentInterface:
        """Create and return an agent of the specified type."""
        pass 