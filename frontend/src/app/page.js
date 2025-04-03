'use client';

import { Container, Paper, Typography, Box, Stack, Grid } from '@mui/material';

export default function Home() {
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
                Chat Interface
              </Typography>
            </Box>
            
            <Box 
              sx={{ 
                flex: 1,
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                bgcolor: 'grey.50',
                gap: 1,
                overflow: 'auto'
              }}
            >
              <Typography variant="body1" color="text.secondary">
                No messages yet
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upload a document to start the conversation
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
