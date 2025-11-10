import { createTheme } from '@mui/material/styles';

export const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',  // Light blue for primary actions
    },
    secondary: {
      main: '#f48fb1',  // Pink for secondary actions
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    success: {
      main: '#66bb6a',  // Green for correct answers
    },
    error: {
      main: '#f44336',  // Red for incorrect answers
    },
  },
  typography: {
    fontFamily: [
      'Noto Sans JP',  // For Japanese text
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: { fontSize: '2rem' },
    h2: { fontSize: '1.5rem' },
    h3: { fontSize: '1.25rem' },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',  // Disable uppercase
        },
      },
    },
  },
});
