import { Box, Typography } from '@mui/material';

export default function Header() {
  return (
    <Box sx={{ 
      borderBottom: 1, 
      borderColor: 'grey.100',
      px: 2,
      py: 1,
      height: '48px',
      display: 'flex',
      alignItems: 'center'
    }}>
      <Typography 
        variant="h3" 
        component="h1"
        sx={{
          color: 'text.primary',
          textAlign: { xs: 'center', md: 'left' },
          fontSize: { xs: '1.25rem', md: '1.5rem' },
          mb: 0,
          fontWeight: 500
        }}
      >
        Kiyo Construction - Bid Leveling
      </Typography>
    </Box>
  );
} 