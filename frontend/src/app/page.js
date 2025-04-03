'use client';

import { Container, Paper, Typography, Box, Stack, Button, TextField, CircularProgress, List, ListItem, ListItemText, Avatar, IconButton } from '@mui/material';
import { useState, useEffect, useRef } from 'react';
import SendIcon from '@mui/icons-material/Send';

export default function Home() {
  const [apiMessage, setApiMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const fetchHelloWorld = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/');
      if (!response.ok) {
        throw new Error(`API responded with status ${response.status}`);
      }
      const data = await response.json();
      setApiMessage(data.message);
    } catch (err) {
      console.error('Error fetching from API:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

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
    setInputMessage('');
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

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  return (
    <Box 
      sx={{ 
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.default',
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <Box sx={{ 
        borderBottom: 1, 
        borderColor: 'grey.100',
        px: 2,
        py: 1,
        height: '48px',
        display: 'flex',
        alignItems: 'center'
      }}>
        <Typography 
          variant="h3" 
          component="h1"
          sx={{
            color: 'text.primary',
            textAlign: { xs: 'center', md: 'left' },
            fontSize: { xs: '1.25rem', md: '1.5rem' },
            mb: 0,
            fontWeight: 500
          }}
        >
          Kiyo Construction - Bid Leveling
        </Typography>
      </Box>
      
      {/* Main Content */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'hidden',
        display: 'flex',
        gap: 1,
        p: 1
      }}>
        {/* Spreadsheet Section */}
        <Box sx={{ flex: 2, minWidth: 0 }}>
          <Paper 
            sx={{ 
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: 'background.paper',
              border: '1px dashed',
              borderColor: 'grey.300'
            }}
          >
            <Stack spacing={2} alignItems="center">
              <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 500 }}>
                Spreadsheet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Google Sheets integration coming soon
              </Typography>
            </Stack>
          </Paper>
        </Box>

        {/* Chat Section */}
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
            
            {/* Messages area */}
            <Box 
              sx={{ 
                flex: 1,
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'grey.50',
                gap: 1,
                overflow: 'auto'
              }}
            >
              {messages.length === 0 ? (
                <Box sx={{ 
                  flex: 1, 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'center', 
                  alignItems: 'center' 
                }}>
                  <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mb: 2 }}>
                    Welcome to the Kiyo Construction Assistant
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
                    Ask me anything about construction materials, techniques, or project planning.
                  </Typography>
                </Box>
              ) : (
                <List sx={{ width: '100%', p: 0 }}>
                  {messages.map((message, index) => (
                    <ListItem 
                      key={index} 
                      sx={{ 
                        p: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: message.sender === 'user' ? 'flex-end' : 'flex-start',
                        mb: 1
                      }}
                    >
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'flex-start',
                        maxWidth: '85%' 
                      }}>
                        {message.sender === 'assistant' && (
                          <Avatar 
                            sx={{ 
                              mr: 1, 
                              mt: 0.5, 
                              bgcolor: 'primary.main', 
                              width: 32, 
                              height: 32 
                            }}
                          >
                            K
                          </Avatar>
                        )}
                        <Paper 
                          sx={{ 
                            p: 1.5, 
                            borderRadius: 2,
                            bgcolor: message.sender === 'user' ? 'primary.main' : 'background.paper',
                            color: message.sender === 'user' ? 'white' : 'text.primary',
                            boxShadow: 1
                          }}
                        >
                          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                            {message.text}
                          </Typography>
                        </Paper>
                        {message.sender === 'user' && (
                          <Avatar 
                            sx={{ 
                              ml: 1, 
                              mt: 0.5, 
                              bgcolor: 'grey.400', 
                              width: 32, 
                              height: 32 
                            }}
                          >
                            U
                          </Avatar>
                        )}
                      </Box>
                    </ListItem>
                  ))}
                  {isTyping && (
                    <ListItem sx={{ p: 1, display: 'flex', alignItems: 'flex-start' }}>
                      <Avatar 
                        sx={{ 
                          mr: 1, 
                          mt: 0.5, 
                          bgcolor: 'primary.main', 
                          width: 32, 
                          height: 32 
                        }}
                      >
                        K
                      </Avatar>
                      <Paper 
                        sx={{ 
                          p: 1.5,
                          borderRadius: 2,
                          bgcolor: 'background.paper',
                          boxShadow: 1,
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <Typography variant="body2" color="text.secondary">
                          Typing...
                        </Typography>
                      </Paper>
                    </ListItem>
                  )}
                  <div ref={messagesEndRef} />
                </List>
              )}
              
              {error && (
                <Paper 
                  sx={{ 
                    p: 2, 
                    mt: 2, 
                    width: '100%', 
                    bgcolor: '#fff8f8',
                    borderLeft: '4px solid',
                    borderColor: 'error.main'
                  }}
                >
                  <Typography variant="body2" color="error.main">
                    Error: {error}
                  </Typography>
                </Paper>
              )}
            </Box>
            
            {/* Message input */}
            <Box 
              component="form" 
              onSubmit={handleSubmit}
              sx={{ 
                p: 2, 
                borderTop: 1, 
                borderColor: 'grey.100',
                bgcolor: 'background.paper'
              }}
            >
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Ask about construction..."
                  size="small"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  disabled={isTyping}
                  sx={{ 
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 3,
                    }
                  }}
                />
                <IconButton 
                  color="primary" 
                  type="submit" 
                  disabled={!inputMessage.trim() || isTyping}
                  sx={{ 
                    bgcolor: 'primary.main', 
                    color: 'white',
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '&.Mui-disabled': {
                      bgcolor: 'grey.300',
                      color: 'grey.500',
                    }
                  }}
                >
                  <SendIcon />
                </IconButton>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
