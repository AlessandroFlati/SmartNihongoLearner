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
  Button,
  AppBar,
  Toolbar,
  IconButton,
} from '@mui/material';
import {
  Home as HomeIcon,
  SportsEsports as GameIcon,
} from '@mui/icons-material';
import { initializeAllData, getVocabularyStats, getCollocationStats } from './services/dataLoader';
import storage from './services/storage';
import { getRecommendedPracticeWords } from './services/collocation';
import { getWordsDueForReview } from './services/srs';
import GameModeSelector from './components/games/GameModeSelector';
import WhatCouldMatch from './components/games/WhatCouldMatch';

function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [initialized, setInitialized] = useState(false);
  const [stats, setStats] = useState({
    vocabulary: null,
    collocations: null,
    database: null,
  });

  // Navigation state
  const [currentScreen, setCurrentScreen] = useState('home'); // home, game-setup, playing
  const [gameConfig, setGameConfig] = useState(null);
  const [currentWord, setCurrentWord] = useState(null);
  const [wordQueue, setWordQueue] = useState([]);

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

  const handleStartGame = async (config) => {
    setGameConfig(config);

    // Get word queue based on selection mode
    let queue = [];
    const wordType = config.mode === 'verb-to-noun' ? 'verb' : 'adjective';

    try {
      if (config.wordSelection === 'recommended') {
        const recommended = await getRecommendedPracticeWords(10);
        queue = recommended
          .filter(c => c.type === wordType)
          .map(c => ({
            id: c.word,
            japanese: c.word,
            reading: c.reading,
            english: c.english,
            type: c.type,
          }));
      } else if (config.wordSelection === 'due') {
        const dueWords = await getWordsDueForReview();
        const vocab = await storage.getVocabularyByType(wordType);
        const dueIds = new Set(dueWords.map(w => w.wordId));
        queue = vocab
          .filter(v => dueIds.has(v.id))
          .slice(0, 10);
      } else {
        // Random
        const vocab = await storage.getVocabularyByType(wordType);
        const shuffled = [...vocab].sort(() => Math.random() - 0.5);
        queue = shuffled.slice(0, 10);
      }

      if (queue.length === 0) {
        setError('No words available for practice. Try a different selection mode.');
        return;
      }

      setWordQueue(queue);
      setCurrentWord(queue[0]);
      setCurrentScreen('playing');
    } catch (err) {
      console.error('Error starting game:', err);
      setError(`Failed to start game: ${err.message}`);
    }
  };

  const handleGameComplete = (results) => {
    console.log('Game results:', results);

    // Move to next word in queue
    const currentIndex = wordQueue.findIndex(w => w.japanese === currentWord.japanese);
    if (currentIndex < wordQueue.length - 1) {
      setCurrentWord(wordQueue[currentIndex + 1]);
    } else {
      // No more words - return to setup
      setCurrentScreen('game-setup');
      setWordQueue([]);
      setCurrentWord(null);
    }
  };

  const handleBackToHome = () => {
    setCurrentScreen('home');
    setGameConfig(null);
    setCurrentWord(null);
    setWordQueue([]);
  };

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
          <Button variant="contained" onClick={handleBackToHome}>
            Back to Home
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={handleBackToHome}
            sx={{ mr: 2 }}
          >
            <HomeIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Smart Nihongo Learner
          </Typography>
          {currentScreen === 'playing' && wordQueue.length > 0 && (
            <Typography variant="body2">
              Word {wordQueue.findIndex(w => w.japanese === currentWord?.japanese) + 1} / {wordQueue.length}
            </Typography>
          )}
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="md" sx={{ mt: 4, mb: 4, flexGrow: 1 }}>
        {currentScreen === 'home' && (
          <Box>
            <Typography variant="h1" component="h1" gutterBottom align="center" sx={{ fontSize: '2.5rem' }}>
              Smart Nihongo Learner
            </Typography>
            <Typography variant="h3" component="h2" gutterBottom align="center" color="text.secondary" sx={{ fontSize: '1.5rem' }}>
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

              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<GameIcon />}
                  onClick={() => setCurrentScreen('game-setup')}
                >
                  Start Playing
                </Button>
              </Box>
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
        )}

        {currentScreen === 'game-setup' && (
          <GameModeSelector onStartGame={handleStartGame} />
        )}

        {currentScreen === 'playing' && currentWord && (
          <WhatCouldMatch
            word={currentWord}
            onComplete={handleGameComplete}
            mode={gameConfig.mode}
          />
        )}
      </Container>
    </Box>
  );
}

export default App;
