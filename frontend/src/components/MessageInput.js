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
        placeholder="Share your bids..."
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isTyping}
        autoComplete="off"
        maxRows={6}
        style={{
          width: '100%',
          resize: 'none',
          padding: '8px 12px',
          borderRadius: '4px',
          border: '1px solid var(--input-border)',
          backgroundColor: 'var(--input-background)',
          color: 'var(--color-text-primary)',
          fontSize: '0.875rem',
          lineHeight: '1.5',
          fontFamily: 'inherit',
          outline: 'none'
        }}
      />
      <IconButton 
        color="primary" 
        type="submit" 
        disabled={!inputMessage.trim() || isTyping}
        sx={{ 
          bgcolor: 'var(--color-surface)', 
          color: 'var(--color-text-primary)',
          border: '1px solid',
          borderColor: 'var(--input-border)',
          borderRadius: '4px',
          padding: '6px',
          alignSelf: 'flex-end',
          height: '36px',
          width: '36px',
          flexShrink: 0,
          '&:hover': {
            bgcolor: 'var(--color-surface)',
            borderColor: 'var(--color-border)',
          },
          '&.Mui-disabled': {
            bgcolor: 'var(--color-surface)',
            color: 'var(--color-text-secondary)',
            opacity: 0.7
          }
        }}
      >
        <SendIcon />
      </IconButton>
    </Box>
  );
} 