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
        bgcolor: 'var(--chat-background)',
        gap: 2,
        overflow: 'auto'
      }}
    >
      {messages.length === 0 ? (
        <Box sx={{ 
          flex: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          justifyContent: 'center', 
          alignItems: 'center',
          color: 'var(--color-text-secondary)'
        }}>
          <Typography 
            variant="body1" 
            sx={{ 
              textAlign: 'center', 
              mb: 1,
              fontSize: '0.9375rem'
            }}
          >
            Welcome to the Construction Assistant
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              textAlign: 'center',
              fontSize: '0.875rem',
              opacity: 0.8
            }}
          >
            Share your recent bids to start the leveling process
          </Typography>
        </Box>
      ) : (
        <List sx={{ width: '100%', p: 0 }}>
          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}
          {isTyping && (
            <ListItem sx={{ p: 1 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'var(--color-text-secondary)',
                  fontSize: '0.75rem',
                  fontStyle: 'italic',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                Your agent is typing
                <CircularProgress size={8} sx={{ color: 'inherit' }} />
              </Typography>
            </ListItem>
          )}
          <div ref={messagesEndRef} />
        </List>
      )}
      
      {error && (
        <Paper 
          elevation={0}
          sx={{ 
            p: 2, 
            mt: 2, 
            width: '100%', 
            bgcolor: '#FFF4F4',
            border: '1px solid',
            borderColor: '#FFA5A5',
            borderRadius: '4px',
            position: 'relative',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Typography 
            variant="body2" 
            sx={{ 
              color: '#D64545',
              fontSize: '0.875rem'
            }}
          >
            Error: {error}
          </Typography>
          <Box 
            component="button"
            onClick={() => document.dispatchEvent(new CustomEvent('dismissError'))}
            sx={{
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              ml: 2,
              p: 0.5,
              borderRadius: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#D64545',
              '&:hover': {
                bgcolor: 'rgba(214, 69, 69, 0.05)'
              }
            }}
            aria-label="Close error message"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </Box>
        </Paper>
      )}
    </Box>
  );
} 