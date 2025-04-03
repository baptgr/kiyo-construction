import { Box, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
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

  return (
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
  );
} 