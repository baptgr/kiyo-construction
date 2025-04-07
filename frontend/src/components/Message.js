import { Box, Typography, Avatar, ListItem } from '@mui/material';

export default function Message({ message }) {
  const isUser = message.sender === 'user';
  
  return (
    <ListItem 
      sx={{ 
        p: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        mb: 0.5
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'flex-start',
        maxWidth: '85%',
        gap: 1.5
      }}>
        {!isUser && (
          <Avatar 
            sx={{ 
              mt: 0.5, 
              bgcolor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              width: 28,
              height: 28,
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            K
          </Avatar>
        )}
        <Box 
          sx={{ 
            p: 1.5,
            borderRadius: '4px',
            bgcolor: isUser ? 'var(--color-surface)' : 'var(--message-background)',
            color: 'var(--color-text-primary)',
            fontSize: '0.875rem',
            lineHeight: 1.5,
            whiteSpace: 'pre-wrap'
          }}
        >
          {message.text}
        </Box>
        {isUser && (
          <Avatar 
            sx={{ 
              mt: 0.5,
              bgcolor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              width: 28,
              height: 28,
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            U
          </Avatar>
        )}
      </Box>
    </ListItem>
  );
} 