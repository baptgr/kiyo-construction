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
        bgcolor: 'background.default',
        overflow: 'hidden'
      }}
    >
      <Header />
      
      {/* Main Content */}
      <Box sx={{ 
        flex: 1, 
        overflow: 'hidden',
        display: 'flex',
        gap: 1,
        p: 1
      }}>
        <SpreadsheetSection />
        <ChatSection />
      </Box>
    </Box>
  );
}
