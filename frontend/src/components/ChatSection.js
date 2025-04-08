import { Box, Paper, Typography } from '@mui/material';
import { useState, useEffect, useCallback } from 'react';
import { useSession } from 'next-auth/react';
import { useSpreadsheet } from '@/context/SpreadsheetContext';
import { useConversation } from '@/context/ConversationContext';
import { useAgentStreamApi } from '@/utils/agentAPI';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const { getStreamResponse } = useAgentStreamApi();
  const { conversationId, startNewConversation } = useConversation();

  // Start a new conversation when component mounts
  useEffect(() => {
    startNewConversation();
  }, []);

  // Add event listener for error dismissal
  useEffect(() => {
    const handleDismissError = () => {
      setError(null);
    };
    document.addEventListener('dismissError', handleDismissError);
    
    return () => {
      document.removeEventListener('dismissError', handleDismissError);
    };
  }, []);

  // Update assistant message text
  const updateAssistantMessage = useCallback((newText) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      if (lastMessage?.sender === 'assistant') {
        lastMessage.text = newText;
      }
      return newMessages;
    });
  }, []);

  // Send a message to the API with streaming
  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      text: messageText,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);
    setError(null);
    
    try {
      // Create an empty assistant message that we'll update as we receive chunks
      const assistantMessage = {
        text: '',
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      const response = await getStreamResponse(messageText, conversationId);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let messageStarted = false;
      let streamFinished = false;

      while (true) {
        const { value, done } = await reader.read();
        
        if (done) {
          if (!streamFinished) {
            setIsTyping(false);
          }
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.trim() === '' || line.startsWith('retry:')) continue;
          
          if (line.startsWith('event:')) {
            const eventType = line.slice(7).trim();
            if (eventType === 'error') {
              messageStarted = false;
              setIsTyping(false);
            } else if (eventType === 'done') {
              streamFinished = true;
              setIsTyping(false);
            }
            continue;
          }
          
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                setError(data.error);
                setIsTyping(false);
                return;
              }
              
              if (data.text) {
                messageStarted = true;
                updateAssistantMessage(data.text);
              }
              
              if (data.finished) {
                streamFinished = true;
                setIsTyping(false);
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
              continue;
            }
          }
        }
      }
      
      if (!messageStarted) {
        throw new Error('No response received from the agent');
      }
      
      setIsTyping(false);
      
    } catch (error) {
      console.error('Error in streaming:', error);
      setError(error.message || 'An error occurred while streaming the response');
      
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage?.sender === 'assistant') {
          lastMessage.text = 'Error: Failed to get response';
          lastMessage.error = true;
        }
        return newMessages;
      });
      
      setIsTyping(false);
    }
  };

  return (
    <Box sx={{ 
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      bgcolor: 'var(--chat-background)',
      overflow: 'hidden'
    }}>
      <Box sx={{ 
        px: 2, 
        py: 1.5,
        borderBottom: '1px solid',
        borderColor: 'var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        bgcolor: 'var(--color-background)'
      }}>
        <Typography 
          variant="h6" 
          sx={{ 
            fontSize: '0.875rem', 
            fontWeight: 500,
            color: 'var(--color-text-primary)'
          }}
        >
          Construction Assistant
        </Typography>
      </Box>
      
      <Box sx={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}>
        <MessageList 
          messages={messages}
          isTyping={isTyping}
          error={error}
        />
        
        <Box sx={{ 
          p: 2,
          borderTop: '1px solid',
          borderColor: 'var(--color-border)',
          bgcolor: 'var(--color-background)'
        }}>
          <MessageInput 
            onSendMessage={sendMessage}
            isTyping={isTyping}
          />
        </Box>
      </Box>
    </Box>
  );
} 