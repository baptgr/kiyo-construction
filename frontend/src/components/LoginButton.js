'use client';

import { Button, Avatar, Box, Menu, MenuItem, Typography } from '@mui/material';
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
    return (
      <Button 
        disabled
        sx={{ 
          color: 'var(--color-text-secondary)',
          fontSize: '0.875rem',
          textTransform: 'none',
          minWidth: 'auto'
        }}
      >
        Loading...
      </Button>
    );
  }

  if (status === 'authenticated' && session?.user) {
    return (
      <Box>
        <Button
          onClick={handleUserMenuClick}
          sx={{ 
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            color: 'var(--color-text-primary)',
            textTransform: 'none',
            fontSize: '0.875rem',
            fontWeight: 400,
            '&:hover': {
              bgcolor: 'var(--color-surface)'
            }
          }}
        >
          <Avatar 
            alt={session.user.name || 'User'} 
            src={session.user.image || ''} 
            sx={{ 
              width: 24, 
              height: 24,
              fontSize: '0.875rem'
            }}
          />
          <span>{session.user.name || 'User'}</span>
        </Button>
        
        <Menu
          anchorEl={anchorEl}
          open={open}
          onClose={handleClose}
          MenuListProps={{
            'aria-labelledby': 'user-menu-button',
          }}
          sx={{
            '& .MuiPaper-root': {
              borderRadius: '4px',
              border: '1px solid',
              borderColor: 'var(--color-border)',
              boxShadow: 'var(--shadow-md)',
              bgcolor: 'var(--color-background)',
              minWidth: '200px'
            }
          }}
        >
          <MenuItem disabled sx={{ opacity: 0.7 }}>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'var(--color-text-secondary)',
                fontSize: '0.8125rem'
              }}
            >
              {session.user.email}
            </Typography>
          </MenuItem>
          <MenuItem 
            onClick={handleLogout} 
            disabled={isLoading}
            sx={{
              color: 'var(--color-text-primary)',
              fontSize: '0.875rem',
              py: 1,
              '&:hover': {
                bgcolor: 'var(--color-surface)'
              }
            }}
          >
            Sign out
          </MenuItem>
        </Menu>
      </Box>
    );
  }

  return (
    <Button 
      variant="text" 
      onClick={handleLoginClick}
      disabled={isLoading}
      sx={{ 
        color: 'var(--color-text-primary)',
        bgcolor: 'var(--color-surface)',
        border: '1px solid',
        borderColor: 'var(--color-border)',
        borderRadius: '4px',
        px: 2,
        py: 1,
        fontSize: '0.875rem',
        fontWeight: 400,
        textTransform: 'none',
        '&:hover': {
          bgcolor: 'var(--color-surface)',
          borderColor: 'var(--color-text-secondary)'
        }
      }}
    >
      Sign in
    </Button>
  );
} 