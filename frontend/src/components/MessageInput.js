import { Box, IconButton, TextareaAutosize } from '@mui/material';
import SendIcon from '../components/SendIcon';
import { useState } from 'react';

export default function MessageInput({ onSendMessage, isTyping }) {
  const [inputMessage, setInputMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Box 
      component="form" 
      onSubmit={handleSubmit}
      sx={{ 
        display: 'flex',
        gap: 1,
        position: 'relative'
      }}
    >
      <TextareaAutosize
        placeholder="Message your agent..."
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isTyping}
        autoComplete="off"
        maxRows={6}
        style={{
          width: '100%',
          resize: 'none',
          padding: '12px',
          borderRadius: '3px',
          border: '1px solid var(--input-border)',
          backgroundColor: 'var(--input-background)',
          color: 'var(--color-text-primary)',
          fontSize: '0.875rem',
          lineHeight: '1.5',
          fontFamily: 'inherit',
          outline: 'none',
          transition: 'border-color 0.2s ease',
        }}
      />
      <IconButton 
        color="primary" 
        type="submit" 
        disabled={!inputMessage.trim() || isTyping}
        sx={{ 
          bgcolor: 'transparent', 
          color: 'var(--color-text-secondary)',
          border: 'none',
          borderRadius: '3px',
          padding: '8px',
          alignSelf: 'flex-end',
          height: '36px',
          width: '36px',
          flexShrink: 0,
          transition: 'all 0.2s ease',
          '&:hover': {
            bgcolor: 'var(--color-surface)',
            color: 'var(--color-text-primary)',
          },
          '&.Mui-disabled': {
            opacity: 0.5,
            color: 'var(--color-text-secondary)'
          }
        }}
      >
        <SendIcon sx={{ fontSize: 20 }} />
      </IconButton>
    </Box>
  );
} 