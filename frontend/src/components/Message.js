import { Box, Typography, Avatar, ListItem } from '@mui/material';
import ReactMarkdown from 'react-markdown';

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
        gap: 1.5,
        width: '100%'
      }}>
        {!isUser && (
          <Avatar 
            sx={{ 
              mt: 0.5, 
              bgcolor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              width: 24,
              height: 24,
              fontSize: '0.875rem',
              fontWeight: 500
            }}
          >
            K
          </Avatar>
        )}
        <Box 
          sx={{ 
            p: isUser ? 1 : 0,
            borderRadius: isUser ? '4px' : '0',
            bgcolor: isUser ? 'var(--color-surface)' : 'transparent',
            color: 'var(--color-text-primary)',
            fontSize: '0.875rem',
            lineHeight: 1.5,
            width: '100%',
            '& .markdown': {
              '& p': {
                m: 0,
                mb: 1.5,
                '&:last-child': {
                  mb: 0
                }
              },
              '& h1, & h2, & h3, & h4, & h5, & h6': {
                fontSize: 'inherit',
                fontWeight: 600,
                m: 0,
                mb: 1,
                color: 'var(--color-text-primary)'
              },
              '& h1': {
                fontSize: '1.1rem'
              },
              '& h2': {
                fontSize: '1rem'
              },
              '& pre': {
                bg: 'var(--color-surface)',
                p: 2,
                borderRadius: '4px',
                overflow: 'auto',
                my: 1
              },
              '& code': {
                fontFamily: 'monospace',
                fontSize: '0.85em',
                p: '2px 4px',
                borderRadius: '3px',
                bg: 'var(--color-surface)'
              },
              '& ul': {
                pl: 0,
                m: 0,
                mb: 1.5,
                listStyleType: 'none',
                '& li': {
                  position: 'relative',
                  pl: 3,
                  mb: 0.75,
                  '&:before': {
                    content: '""',
                    width: '4px',
                    height: '4px',
                    bgcolor: 'var(--color-text-secondary)',
                    borderRadius: '50%',
                    position: 'absolute',
                    left: '8px',
                    top: '0.6em',
                    transform: 'translateY(-50%)'
                  },
                  '&:last-child': {
                    mb: 0
                  }
                }
              },
              '& ol': {
                pl: 0,
                m: 0,
                mb: 1.5,
                listStyleType: 'none',
                counterReset: 'section',
                '& > li': {
                  position: 'relative',
                  pl: 3,
                  mb: 0.75,
                  counterIncrement: 'section',
                  '&:before': {
                    content: 'counter(section) "."',
                    position: 'absolute',
                    left: 0,
                    color: 'var(--color-text-secondary)',
                    fontWeight: 400
                  },
                  '& ol': {
                    counterReset: 'subsection',
                    mt: 0.75,
                    '& > li': {
                      pl: 4,
                      counterIncrement: 'subsection',
                      '&:before': {
                        content: 'counter(section) "." counter(subsection) "."',
                        left: 0
                      }
                    }
                  }
                }
              },
              '& strong': {
                fontWeight: 600,
                color: 'var(--color-text-primary)'
              },
              '& blockquote': {
                borderLeft: '3px solid var(--color-border)',
                pl: 2,
                my: 1,
                color: 'var(--color-text-secondary)'
              }
            }
          }}
        >
          {isUser ? (
            message.text
          ) : (
            <div className="markdown">
              <ReactMarkdown>{message.text}</ReactMarkdown>
            </div>
          )}
        </Box>
        {isUser && (
          <Avatar 
            sx={{ 
              mt: 0.5,
              bgcolor: 'var(--color-surface)',
              color: 'var(--color-text-primary)',
              width: 24,
              height: 24,
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