import { Box, Paper, Typography } from '@mui/material';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useSpreadsheet } from '@/context/SpreadsheetContext';
import { useAgentStreamApi } from '@/utils/agentAPI';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const { getStreamResponse } = useAgentStreamApi();

  // Add event listener for error dismissal
  useEffect(() => {
    const handleDismissError = () => setError(null);
    document.addEventListener('dismissError', handleDismissError);
    
    return () => {
      document.removeEventListener('dismissError', handleDismissError);
    };
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
      
      // Get streaming response using our hook
      const response = await getStreamResponse(messageText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.text) {
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.sender === 'assistant') {
                    lastMessage.text += data.text;
                  }
                  return newMessages;
                });
              }
              if (data.finished) {
                setIsTyping(false);
                return;
              }
              if (data.error) {
                throw new Error(data.error);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setError(error.message || 'An error occurred');
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