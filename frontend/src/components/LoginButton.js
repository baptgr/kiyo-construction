'use client';

import { Button, Typography, Box } from '@mui/material';
import { signIn, signOut } from 'next-auth/react';
import { useEffect, useState } from 'react';
import { useSession } from 'next-auth/react';

export default function LoginButton() {
  const { data: session, status } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    console.log('Session status:', status);
    console.log('Session data:', session);
  }, [status, session]);

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      await signIn('google', { callbackUrl: '/' });
    } catch (error) {
      console.error('Sign in error:', error);
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    setIsLoading(true);
    try {
      await signOut({ callbackUrl: '/' });
    } catch (error) {
      console.error('Sign out error:', error);
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
        Status: {status}
      </Typography>
      
      {status === 'authenticated' ? (
        <Button 
          variant="outlined" 
          color="primary" 
          onClick={handleLogout}
          disabled={isLoading}
        >
          Logout
        </Button>
      ) : (
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleLogin}
          disabled={isLoading}
        >
          Sign in with Google
        </Button>
      )}
    </Box>
  );
} 