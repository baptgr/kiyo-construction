import { Box, Paper, Typography } from '@mui/material';
import { useState } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

export default function ChatSection() {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

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
    
    try {
      // Create an empty assistant message that we'll update as we receive chunks
      const assistantMessage = {
        text: '',
        sender: 'assistant',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Call the streaming endpoint
      const response = await fetch('http://localhost:8000/api/chat/stream/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: messageText })
      });
      
      if (!response.ok) {
        throw new Error(`API responded with status ${response.status}`);
      }
      
      // Use the EventSource API to handle SSE properly
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let debugOutput = [];
      
      while (true) {
        const { value, done } = await reader.read();
        
        if (done) {
          console.log("Streaming complete. Debug output:", debugOutput);
          setIsTyping(false);
          break;
        }
        
        // Decode the chunk and add to buffer
        const newText = decoder.decode(value, { stream: true });
        buffer += newText;
        
        // Log the raw chunk for debugging
        console.log("Raw SSE chunk received:", newText);
        debugOutput.push(newText);
        
        // Process complete SSE events in the buffer
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep the incomplete event in the buffer
        
        for (const eventText of lines) {
          if (!eventText.trim()) continue;
          
          // Parse event type and data
          const eventLines = eventText.split('\n');
          console.log("Event lines:", eventLines);
          
          const eventType = eventLines.find(line => line.startsWith('event:'))?.substring(6).trim();
          const dataLine = eventLines.find(line => line.startsWith('data:'))?.substring(5).trim();
          
          console.log("Parsed SSE event:", { eventType, dataLine });
          
          if (!eventType || !dataLine) continue;
          
          try {
            const data = JSON.parse(dataLine);
            console.log("Parsed data:", data);
            
            if (eventType === 'chunk' && data.text) {
              console.log("Received text chunk:", data.text);
              // Update the last message with the new text chunk
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage.sender === 'assistant') {
                  // Check if this text is already at the end of the message
                  // to prevent any duplicate content
                  if (!lastMessage.text.endsWith(data.text)) {
                    lastMessage.text += data.text;
                  } else {
                    console.log("Prevented duplicate content:", data.text);
                  }
                }
                return newMessages;
              });
            } else if (eventType === 'done') {
              console.log("Received done event");
              setIsTyping(false);
            } else if (eventType === 'error' && data.error) {
              console.error("Received error event:", data.error);
              setError(data.error);
              setIsTyping(false);
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, dataLine);
          }
        }
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(err.message);
      setIsTyping(false);
    }
  };

  return (
    <Box sx={{ flex: 1, minWidth: 0 }}>
      <Paper 
        sx={{ 
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper',
          overflow: 'hidden'
        }}
      >
        <Box sx={{ 
          px: 2, 
          py: 1, 
          borderBottom: 1, 
          borderColor: 'grey.100',
          height: '40px',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Typography variant="h5" color="text.primary" sx={{ fontSize: '1.1rem', fontWeight: 500 }}>
            Construction Assistant
          </Typography>
        </Box>
        
        <MessageList 
          messages={messages}
          isTyping={isTyping}
          error={error}
        />
        
        <MessageInput 
          onSendMessage={sendMessage}
          isTyping={isTyping}
        />
      </Paper>
    </Box>
  );
} 