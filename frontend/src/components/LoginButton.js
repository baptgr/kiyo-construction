'use client';

import { Button, Avatar, Chip, Box, Menu, MenuItem, Typography } from '@mui/material';
import { signIn, signOut } from 'next-auth/react';
import { useState } from 'react';
import { useSession } from 'next-auth/react';

export default function LoginButton() {
  const { data: session, status } = useSession();
  const [isLoading, setIsLoading] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);
  
  const handleLoginClick = async () => {
    setIsLoading(true);
    try {
      await signIn('google', { callbackUrl: '/' });
    } catch (error) {
      console.error('Sign in error:', error);
      setIsLoading(false);
    }
  };

  const handleUserMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    setIsLoading(true);
    handleClose();
    try {
      await signOut({ callbackUrl: '/' });
    } catch (error) {
      console.error('Sign out error:', error);
      setIsLoading(false);
    }
  };

  if (status === 'loading') {
    return <Chip 
      label="Authenticating..." 
      color="default" 
      size="medium" 
      sx={{ 
        borderRadius: '16px',
        px: 1
      }}
    />;
  }

  if (status === 'authenticated' && session?.user) {
    return (
      <Box>
        <Chip
          avatar={
            <Avatar 
              alt={session.user.name || 'User'} 
              src={session.user.image || ''} 
              sx={{ width: 24, height: 24 }}
            />
          }
          label={session.user.name || 'User'}
          onClick={handleUserMenuClick}
          color="primary"
          variant="outlined"
          sx={{ 
            borderRadius: '16px',
            px: 1,
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'rgba(25, 118, 210, 0.04)'
            }
          }}
        />
        
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          MenuListProps={{
            'aria-labelledby': 'user-menu-button',
          }}
        >
          <MenuItem disabled>
            <Typography variant="caption" color="textSecondary" sx={{ fontSize: '0.75rem' }}>
              {session.user.email}
            </Typography>
          </MenuItem>
          <MenuItem onClick={handleLogout} disabled={isLoading}>
            Logout
          </MenuItem>
        </Menu>
      </Box>
    );
  }

  return (
    <Button 
      variant="contained" 
      color="primary" 
      onClick={handleLoginClick}
      disabled={isLoading}
      sx={{ 
        borderRadius: '20px',
        px: 2,
        fontWeight: 500,
        textTransform: 'none'
      }}
    >
      Sign in with Google
    </Button>
  );
} 