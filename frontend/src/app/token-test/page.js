'use client';

import { useSession } from 'next-auth/react';
import { useState } from 'react';
import { Button, Typography, Paper, Box, CircularProgress } from '@mui/material';

export default function TokenTestPage() {
  const { data: session, status } = useSession();
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testToken = async () => {
    setLoading(true);
    try {
      if (!session?.accessToken) {
        throw new Error('No access token available');
      }

      const response = await fetch('https://sheets.googleapis.com/v4/spreadsheets', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          properties: { title: 'Test Sheet' }
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setTestResult({
          success: true,
          message: 'Successfully created sheet!',
          sheetId: data.spreadsheetId,
          sheetUrl: `https://docs.google.com/spreadsheets/d/${data.spreadsheetId}/edit`
        });
      } else {
        const errorData = await response.json();
        setTestResult({
          success: false,
          message: 'API call failed',
          error: errorData.error?.message || `HTTP error ${response.status}`
        });
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Error testing token',
        error: error.message
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>Google Access Token Test</Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Session Status: {status}</Typography>
        
        {status === 'authenticated' ? (
          <>
            <Typography variant="body1">
              Access Token Available: {session?.accessToken ? 'Yes' : 'No'}
            </Typography>
            <Typography variant="body1">
              User: {session?.user?.email || 'Unknown'}
            </Typography>
          </>
        ) : status === 'loading' ? (
          <CircularProgress size={24} />
        ) : (
          <Typography variant="body1" color="error">
            Not authenticated. Please sign in to test the token.
          </Typography>
        )}
      </Paper>
      
      {testResult && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" color={testResult.success ? 'success.main' : 'error.main'}>
            {testResult.message}
          </Typography>
          {testResult.sheetUrl && (
            <Typography variant="body1" component="a" href={testResult.sheetUrl} target="_blank">
              View Created Sheet
            </Typography>
          )}
          {testResult.error && (
            <Typography variant="body1" color="error">
              Error: {testResult.error}
            </Typography>
          )}
        </Paper>
      )}
      
      <Button 
        variant="contained" 
        onClick={testToken} 
        disabled={status !== 'authenticated' || loading}
      >
        {loading ? <CircularProgress size={24} /> : 'Test Token'}
      </Button>
    </Box>
  );
} 