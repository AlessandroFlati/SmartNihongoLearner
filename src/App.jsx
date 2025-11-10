import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { initializeAllData, getVocabularyStats, getCollocationStats } from './services/dataLoader';
import storage from './services/storage';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [stats, setStats] = useState({
    vocabulary: null,
    collocations: null,
    database: null,
  });

  useEffect(() => {
    const initialize = async () => {
      try {
        setLoading(true);

        // Initialize data from JSON files
        const success = await initializeAllData();

        if (success) {
          // Load statistics
          const [vocabStats, collocStats, dbInfo] = await Promise.all([
            getVocabularyStats(),
            getCollocationStats(),
            storage.getDatabaseInfo(),
          ]);

          setStats({
            vocabulary: vocabStats,
            collocations: collocStats,
            database: dbInfo,
          });

          setInitialized(true);
        } else {
          setError('Failed to initialize data. Please refresh the page.');
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setError(`Error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, []);

  if (loading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ my: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="h6" sx={{ mt: 2 }} color="text.secondary">
            Loading vocabulary data...
          </Typography>
          <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">
            First-time setup may take a few seconds
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h1" component="h1" gutterBottom align="center">
          Smart Nihongo Learner
        </Typography>
        <Typography variant="h3" component="h2" gutterBottom align="center" color="text.secondary">
          スマート日本語学習
        </Typography>

        {initialized && (
          <Alert severity="success" sx={{ mt: 2, mb: 3 }}>
            Data loaded successfully! All {stats.database.vocabularyCount} words and{' '}
            {stats.database.collocationsCount} collocations are ready.
          </Alert>
        )}

        <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Welcome to Smart Nihongo Learner
          </Typography>
          <Typography variant="body1" paragraph>
            Learn Japanese vocabulary through context-based collocations. Master word combinations
            the way native speakers use them.
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Core services are initialized. Game components will be added next.
          </Typography>
        </Paper>

        {stats.vocabulary && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Vocabulary Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Total Words
                    </Typography>
                    <Typography variant="h4">
                      {stats.vocabulary.total}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Nouns
                    </Typography>
                    <Typography variant="h4">
                      {stats.vocabulary.byType.noun || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Verbs
                    </Typography>
                    <Typography variant="h4">
                      {stats.vocabulary.byType.verb || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Adjectives
                    </Typography>
                    <Typography variant="h4">
                      {stats.vocabulary.byType.adjective || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        {stats.collocations && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
              Collocation Database
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Total Entries
                    </Typography>
                    <Typography variant="h4">
                      {stats.collocations.total}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6}>
                <Card>
                  <CardContent>
                    <Typography color="text.secondary" gutterBottom variant="body2">
                      Total Pairs
                    </Typography>
                    <Typography variant="h4">
                      {stats.collocations.totalPairs}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        )}

        <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="caption" display="block" color="text.secondary" align="center">
            100% Serverless - All data stored in your browser
          </Typography>
          <Typography variant="caption" display="block" color="text.secondary" align="center">
            Your progress persists across sessions (even when browser is shut down)
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}

export default App;
