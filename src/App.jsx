import { Container, Typography, Box, Paper } from '@mui/material';

function App() {
  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h1" component="h1" gutterBottom align="center">
          Smart Nihongo Learner
        </Typography>
        <Typography variant="h3" component="h2" gutterBottom align="center" color="text.secondary">
          スマート日本語学習
        </Typography>

        <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Welcome to Smart Nihongo Learner
          </Typography>
          <Typography variant="body1" paragraph>
            Learn Japanese vocabulary through context-based collocations.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Application is initializing... Core services will be added next.
          </Typography>
        </Paper>

        <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="caption" display="block" color="text.secondary" align="center">
            100% Serverless - All data stored in your browser
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default App;
