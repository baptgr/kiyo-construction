import { Box, Paper, Typography, Avatar, ListItem } from '@mui/material';

export default function Message({ message }) {
  const isUser = message.sender === 'user';
  
  return (
    <ListItem 
      sx={{ 
        p: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        mb: 1
      }}
    >
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'flex-start',
        maxWidth: '85%' 
      }}>
        {!isUser && (
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
            bgcolor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'white' : 'text.primary',
            boxShadow: 1
          }}
        >
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {message.text}
          </Typography>
        </Paper>
        {isUser && (
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
  );
} 