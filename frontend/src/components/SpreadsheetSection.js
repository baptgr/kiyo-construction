'use client';

import { Box, Paper, Typography, Stack, CircularProgress, Button, TextField, Alert, Input } from '@mui/material';
import { useSpreadsheet } from '@/context/SpreadsheetContext';
import { useSession } from 'next-auth/react';
import { useState, useRef } from 'react';

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

  // State for template upload
  const [templateFile, setTemplateFile] = useState(null);
  const [isCreatingFromTemplate, setIsCreatingFromTemplate] = useState(false);
  const [templateError, setTemplateError] = useState(null);
  const fileInputRef = useRef(null); // Ref for hidden file input

  // Handle manual spreadsheet ID entry
  const handleManualEntry = () => {
    if (manualSheetId && manualSheetId.trim().length > 10) {
      setSpreadsheetId(manualSheetId.trim());
    }
  };

  // Handle file selection - NOW triggers creation immediately
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    // Reset file input value so the same file can be selected again if needed
    if(event.target) {
      event.target.value = null;
    }
    if (file) {
      if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') {
        // Clear previous errors/state before starting
        setTemplateError(null);
        setTemplateFile(file); // Keep track of the file potentially needed for display?
        // Immediately attempt to create the sheet
        handleCreateFromTemplate(file); 
      } else {
        setTemplateFile(null);
        setTemplateError('Invalid file type. Please select an XLSX file.');
        // TODO: Display this error more prominently, maybe a toast/snackbar?
        // Since the trigger is now in the header, the initial screen error display won't work.
        alert('Invalid file type. Please select an XLSX file.'); // Temporary alert
      }
    }
  };

  // Trigger hidden file input click
  const handleUploadButtonClick = () => {
    fileInputRef.current.click();
  };

  // Handle creating sheet from template - NOW accepts file argument
  const handleCreateFromTemplate = async (fileToUpload) => {
    if (!fileToUpload) {
      console.error("handleCreateFromTemplate called without a file.");
      return; // Should not happen if called from handleFileChange
    }

    setIsCreatingFromTemplate(true);
    setTemplateError(null);

    const formData = new FormData();
    formData.append('templateFile', fileToUpload);

    try {
      const response = await fetch('/api/google/create-sheet-from-template', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`);
      }

      // Successfully created, update the spreadsheet ID
      setSpreadsheetId(data.spreadsheetId);
      setTemplateFile(null); // Clear file state

    } catch (err) {
      console.error("Error creating from template:", err);
      setTemplateError(err.message || 'Failed to create spreadsheet from template.');
      // TODO: Display this error more prominently (toast/snackbar)
      alert(`Error creating sheet: ${err.message || 'Unknown error'}`); // Temporary alert
      setTemplateFile(null); // Clear file state on error too
    } finally {
      setIsCreatingFromTemplate(false);
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

  // Combined loading state
  const showLoading = isLoading || isCreatingFromTemplate;
  // Adjust loading text slightly
  const loadingText = isLoading 
    ? 'Creating new spreadsheet...' 
    : isCreatingFromTemplate 
    ? 'Creating from template...' 
    : ''; // Should not be visible if neither is true

  if (showLoading) {
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
              {loadingText}
            </Typography>
          </Stack>
        </Paper>
      </Box>
    );
  }

  // Display general error OR template error
  const displayError = error || templateError;

  if (displayError && !spreadsheetId) { // Show errors only if no sheet is loaded
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
              {error ? 'Error Creating Spreadsheet' : 'Error Creating From Template'}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
              {displayError}
            </Typography>

            {/* Conditional Retry/Upload Buttons based on error type */}
            {error && 
              <Button 
                variant="contained" 
                color="primary" 
                onClick={retryCreateSpreadsheet}
              >
                Retry Creation
              </Button>
            }
            {templateError && 
              <Button 
                variant="contained" 
                color="primary" 
                onClick={handleUploadButtonClick} // Let user try uploading again
              >
                Select Different Template
              </Button>
            }
            
            {/* Keep manual entry as an option */}
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

  // Initial state: No spreadsheet ID, not loading, no major error
  if (!spreadsheetId) {
    return (
      <Box sx={{ flex: 2, minWidth: 0 }}>
        {/* Ensure hidden file input is rendered */} 
        <Input 
          type="file"
          accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          onChange={handleFileChange}
          sx={{ display: 'none' }}
          inputRef={fileInputRef}
        />
        <Paper 
          sx={{ 
            height: '100%',
            display: 'flex',
            flexDirection: 'column', // Changed to column
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'background.paper',
            border: '1px dashed',
            borderColor: 'grey.300'
          }}
        >
          <Stack spacing={2.5} alignItems="center" sx={{ p: 3, maxWidth: '80%' }}>
            <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 500 }}>
              Spreadsheet Setup
            </Typography>
            
            {/* Option 1: Create New Blank */}
            <Button 
              variant="contained" 
              color="primary" 
              onClick={createNewSpreadsheet}
              disabled={isLoading} 
              sx={{ width: '250px' }}
            >
              Create New Blank Sheet
            </Button>

            {/* Option 3: Manual Entry */}
            <Typography variant="subtitle2" sx={{ pt: 1 }}>
              Or use an existing sheet:
            </Typography>
            <Stack direction="row" spacing={1} sx={{ width: '250px' }}>
              <TextField
                size="small"
                fullWidth
                placeholder="Paste Google Sheet ID"
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
            Create New Blank
          </Button>
          <Button 
            variant="text" 
            size="small"
            onClick={handleUploadButtonClick} // Re-use the function that clicks the hidden input
            disabled={isCreatingFromTemplate || isLoading} // Disable if any loading is happening
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
            Create from Template
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
      {/* Ensure hidden file input is rendered even when sheet is loaded */} 
      <Input 
        type="file"
        accept=".xlsx, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        onChange={handleFileChange}
        sx={{ display: 'none', position: 'absolute' }} // Keep it out of layout
        inputRef={fileInputRef}
      />
    </Box>
  );
} 