'use client';

import { Box } from '@mui/material';
import Header from '../components/Header';
import SpreadsheetSection from '../components/SpreadsheetSection';
import ChatSection from '../components/ChatSection';

export default function Home() {
  return (
    <Box 
      sx={{ 
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'var(--color-background)',
        overflow: 'hidden'
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
          width: '400px',
          flexShrink: 0,
          borderRight: '1px solid',
          borderColor: 'var(--color-border)',
          bgcolor: 'var(--color-background)',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <ChatSection />
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
