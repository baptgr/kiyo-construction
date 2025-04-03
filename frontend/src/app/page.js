'use client';

import { Container, Paper, Typography, Box, Stack, Button } from '@mui/material';
import { useState, useEffect } from 'react';

export default function Home() {
  const [apiMessage, setApiMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
              <Button 
                variant="contained" 
                color="primary" 
                onClick={fetchHelloWorld}
                disabled={loading}
              >
                {loading ? 'Loading...' : 'Call Hello World API'}
              </Button>
              
              {apiMessage && (
                <Paper 
                  sx={{ 
                    p: 2, 
                    mt: 2, 
                    width: '100%', 
                    bgcolor: 'background.paper',
                    borderLeft: '4px solid',
                    borderColor: 'primary.main'
                  }}
                >
                  <Typography variant="body1">
                    {apiMessage}
                  </Typography>
                </Paper>
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

              {!apiMessage && !error && !loading && (
                <Typography variant="body2" color="text.secondary">
                  Click the button to call the API
                </Typography>
              )}
            </Box>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}
