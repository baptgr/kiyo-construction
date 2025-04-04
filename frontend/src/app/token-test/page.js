'use client';

import { useSession } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { Button, Typography, Paper, Box, CircularProgress } from '@mui/material';

export default function TokenTestPage() {
  const { data: session, status } = useSession();
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testToken = async () => {
    setLoading(true);
    try {
      // Display what token we have
      console.log('Session in token test page:', {
        status,
        hasSession: !!session,
        hasAccessToken: !!session?.accessToken,
        tokenFirstChars: session?.accessToken ? session.accessToken.substring(0, 10) + '...' : 'none'
      });

      // Test the token with a simple Google Sheets API call
      if (session?.accessToken) {
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
          const errorText = await response.text();
          let errorData;
          try {
            errorData = JSON.parse(errorText);
          } catch (e) {
            errorData = { rawText: errorText };
          }
          
          setTestResult({
            success: false,
            message: 'API call failed',
            error: errorData.error?.message || `HTTP error ${response.status}`,
            status: response.status
          });
        }
      } else {
        setTestResult({
          success: false,
          message: 'No access token available',
          sessionStatus: status
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
              Access Token: {session?.accessToken ? (
                <span style={{fontFamily: 'monospace'}}>{session.accessToken.substring(0, 15)}...</span>
              ) : 'Not found'}
            </Typography>
            
            <Typography variant="body1">
              User: {session?.user?.name || 'Unknown'}
            </Typography>
            
            <Typography variant="body1">
              Email: {session?.user?.email || 'Unknown'}
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
      
      <Button 
        variant="contained" 
        onClick={testToken} 
        disabled={status !== 'authenticated' || loading}
        sx={{ mr: 2 }}
      >
        {loading ? <CircularProgress size={24} /> : 'Test Token with Google Sheets API'}
      </Button>
      
      {testResult && (
        <Paper sx={{ p: 3, mt: 3, bgcolor: testResult.success ? '#e8f5e9' : '#ffebee' }}>
          <Typography variant="h6" gutterBottom>
            {testResult.success ? 'Success!' : 'Error'}
          </Typography>
          
          <Typography variant="body1" gutterBottom>
            {testResult.message}
          </Typography>
          
          {testResult.error && (
            <Typography variant="body2" color="error" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
              {testResult.error}
            </Typography>
          )}
          
          {testResult.sheetId && (
            <>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Sheet ID: {testResult.sheetId}
              </Typography>
              <Typography variant="body2">
                <a href={testResult.sheetUrl} target="_blank" rel="noopener noreferrer">
                  Open Sheet
                </a>
              </Typography>
            </>
          )}
        </Paper>
      )}
    </Box>
  );
} 