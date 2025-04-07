'use client';

import { Box } from '@mui/material';
import Header from '../components/Header';
import SpreadsheetSection from '../components/SpreadsheetSection';
import ChatSection from '../components/ChatSection';
import { useState, useCallback } from 'react';

export default function Home() {
  const [chatWidth, setChatWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
    
    const startX = e.pageX;
    const startWidth = chatWidth;
    
    const handleMouseMove = (e) => {
      const newWidth = Math.max(280, Math.min(800, startWidth + (e.pageX - startX)));
      setChatWidth(newWidth);
    };
    
    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      setIsResizing(false);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [chatWidth]);

  return (
    <Box 
      sx={{ 
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'var(--color-background)',
        overflow: 'hidden',
        userSelect: isResizing ? 'none' : 'auto'
      }}
    >
      <Header />
      
      {/* Main Content */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'hidden',
        display: 'flex',
        bgcolor: 'var(--color-surface)'
      }}>
        <Box sx={{ 
          width: chatWidth,
          flexShrink: 0,
          borderRight: '1px solid',
          borderColor: 'var(--color-border)',
          bgcolor: 'var(--color-background)',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative'
        }}>
          <ChatSection />
          {/* Resizer Handle */}
          <Box
            onMouseDown={handleMouseDown}
            sx={{
              position: 'absolute',
              right: -3,
              top: 0,
              bottom: 0,
              width: 6,
              cursor: 'col-resize',
              '&:hover': {
                bgcolor: 'var(--color-border)'
              },
              '&:active': {
                bgcolor: 'var(--color-border)'
              },
              ...(isResizing && {
                bgcolor: 'var(--color-border)'
              })
            }}
          />
        </Box>
        <Box sx={{ 
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          minWidth: 0,
          bgcolor: 'var(--color-background)'
        }}>
          <SpreadsheetSection />
        </Box>
      </Box>
    </Box>
  );
}
