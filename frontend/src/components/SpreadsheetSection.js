'use client';

import { Box, Paper, Typography, Stack, CircularProgress, Button, TextField } from '@mui/material';
import { useSpreadsheet } from '@/context/SpreadsheetContext';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

export default function SpreadsheetSection() {
  const { data: session, status: authStatus } = useSession();
  const { 
    spreadsheetId, 
    isLoading, 
    error, 
    retryCreateSpreadsheet, 
    createNewSpreadsheet,
    setSpreadsheetId 
  } = useSpreadsheet();
  const [manualSheetId, setManualSheetId] = useState('');

  // Handle manual spreadsheet ID entry
  const handleManualEntry = () => {
    if (manualSheetId && manualSheetId.trim().length > 10) {
      setSpreadsheetId(manualSheetId.trim());
    }
  };

  if (authStatus === 'unauthenticated') {
    return (
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
              Please sign in to access Google Sheets
            </Typography>
          </Stack>
        </Paper>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box sx={{ flex: 2, minWidth: 0 }}>
        <Paper 
          sx={{ 
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'background.paper'
          }}
        >
          <Stack spacing={2} alignItems="center">
            <CircularProgress size={40} />
            <Typography variant="body2" color="text.secondary">
              Creating spreadsheet...
            </Typography>
          </Stack>
        </Paper>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ flex: 2, minWidth: 0 }}>
        <Paper 
          sx={{ 
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'background.paper',
            border: '1px solid',
            borderColor: 'error.light'
          }}
        >
          <Stack spacing={2} alignItems="center" sx={{ p: 3, maxWidth: '80%' }}>
            <Typography variant="h5" color="error" sx={{ fontWeight: 500 }}>
              Error Creating Spreadsheet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {error}
            </Typography>

            <Button 
              variant="contained" 
              color="primary" 
              onClick={retryCreateSpreadsheet}
            >
              Retry
            </Button>
            
            <Typography variant="subtitle2" sx={{ mt: 2 }}>
              Or enter a spreadsheet ID manually:
            </Typography>
            
            <Stack direction="row" spacing={1} sx={{ width: '100%' }}>
              <TextField
                size="small"
                fullWidth
                placeholder="Enter Google Sheet ID"
                value={manualSheetId}
                onChange={(e) => setManualSheetId(e.target.value)}
              />
              <Button variant="outlined" onClick={handleManualEntry}>Use</Button>
            </Stack>
          </Stack>
        </Paper>
      </Box>
    );
  }

  if (!spreadsheetId) {
    return (
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
          <Stack spacing={2} alignItems="center" sx={{ p: 3, maxWidth: '80%' }}>
            <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 500 }}>
              Spreadsheet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Initializing Google Sheets...
            </Typography>

            <Button 
              variant="contained" 
              color="primary" 
              onClick={retryCreateSpreadsheet}
            >
              Retry Creation
            </Button>
            
            <Typography variant="subtitle2" sx={{ mt: 2 }}>
              Or enter a spreadsheet ID manually:
            </Typography>
            
            <Stack direction="row" spacing={1} sx={{ width: '100%' }}>
              <TextField
                size="small"
                fullWidth
                placeholder="Enter Google Sheet ID"
                value={manualSheetId}
                onChange={(e) => setManualSheetId(e.target.value)}
              />
              <Button variant="outlined" onClick={handleManualEntry}>Use</Button>
            </Stack>
            
            <Typography variant="caption" color="text.secondary">
              You can enter an existing Google Sheet ID or create a new sheet and paste its ID here.
            </Typography>
          </Stack>
        </Paper>
      </Box>
    );
  }

  // When we have a spreadsheet ID, show the embedded sheet
  return (
    <Box sx={{ flex: 2, minWidth: 0, display: 'flex', flexDirection: 'column' }}>
      <Box 
        sx={{ 
          p: 2,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid',
          borderColor: 'var(--color-border)',
          bgcolor: 'var(--color-background)',
          height: '48px'
        }}
      >
        <Typography 
          variant="subtitle1" 
          sx={{ 
            fontWeight: 500,
            fontSize: '0.875rem',
            color: 'var(--color-text-primary)'
          }}
        >
          Bid Comparison Sheet
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button 
            variant="text" 
            size="small"
            onClick={() => {
              navigator.clipboard.writeText(spreadsheetId);
            }}
            sx={{ 
              color: 'var(--color-text-secondary)',
              textTransform: 'none',
              fontSize: '0.8125rem',
              '&:hover': {
                bgcolor: 'var(--color-surface)',
                color: 'var(--color-text-primary)'
              }
            }}
          >
            Get ID
          </Button>
          <Button 
            variant="text" 
            size="small"
            onClick={createNewSpreadsheet}
            sx={{ 
              color: 'var(--color-text-secondary)',
              textTransform: 'none',
              fontSize: '0.8125rem',
              '&:hover': {
                bgcolor: 'var(--color-surface)',
                color: 'var(--color-text-primary)'
              }
            }}
          >
            Create New
          </Button>
          <Button 
            variant="text" 
            size="small"
            onClick={() => window.open(`https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`, '_blank')}
            sx={{ 
              color: 'var(--color-text-secondary)',
              textTransform: 'none',
              fontSize: '0.8125rem',
              '&:hover': {
                bgcolor: 'var(--color-surface)',
                color: 'var(--color-text-primary)'
              }
            }}
          >
            Open in New Tab
          </Button>
        </Box>
      </Box>
      
      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'hidden',
        bgcolor: 'var(--color-background)',
        position: 'relative'
      }}>
        <iframe 
          src={`https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit?usp=sharing&embedded=true&rm=demo`}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            background: 'var(--color-background)'
          }}
          title="Google Sheet"
          allowFullScreen
        />
      </Box>
    </Box>
  );
} 