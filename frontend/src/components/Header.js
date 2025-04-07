import { Box, Typography } from '@mui/material';
import LoginButton from './LoginButton';

export default function Header() {
  return (
    <Box sx={{ 
      borderBottom: '1px solid',
      borderColor: 'var(--color-border)',
      px: 3,
      py: 2,
      height: '56px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      bgcolor: 'var(--color-background)',
      position: 'relative',
      zIndex: 1000
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography 
          variant="h1" 
          component="h1"
          sx={{
            color: 'var(--color-text-primary)',
            fontSize: '1.125rem',
            fontWeight: 600,
            letterSpacing: '-0.025em',
            m: 0
          }}
        >
          Kiyo Construction
        </Typography>
        <Typography
          component="span"
          sx={{
            color: 'var(--color-text-secondary)',
            fontSize: '0.875rem',
            fontWeight: 400
          }}
        >
          /
        </Typography>
        <Typography
          component="span"
          sx={{
            color: 'var(--color-text-secondary)',
            fontSize: '0.875rem',
            fontWeight: 400
          }}
        >
          Bid Leveling
        </Typography>
      </Box>
      
      <LoginButton />
    </Box>
  );
} 