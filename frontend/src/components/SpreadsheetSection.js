import { Box, Paper, Typography, Stack } from '@mui/material';

export default function SpreadsheetSection() {
  return (
    <Box sx={{ flex: 2, minWidth: 0 }}>
      <Paper 
        sx={{ 
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.paper',
          border: '1px dashed',
          borderColor: 'grey.300'
        }}
      >
        <Stack spacing={2} alignItems="center">
          <Typography variant="h5" color="text.secondary" sx={{ fontWeight: 500 }}>
            Spreadsheet
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Google Sheets integration coming soon
          </Typography>
        </Stack>
      </Paper>
    </Box>
  );
} 