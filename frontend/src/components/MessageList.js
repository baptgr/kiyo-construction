import { Box, List, ListItem, Typography, Paper, Avatar, CircularProgress } from '@mui/material';
import { useRef, useEffect } from 'react';
import Message from './Message';

export default function MessageList({ messages, isTyping, error }) {
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
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
            <Message key={index} message={message} />
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
  );
} 