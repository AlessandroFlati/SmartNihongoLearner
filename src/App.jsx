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
  ButtonGroup,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import {
  Home as HomeIcon,
  SportsEsports as GameIcon,
  CheckCircle as CheckIcon,
  DeleteForever as DeleteIcon,
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { initializeAllData, getVocabularyStats, getCollocationStats } from './services/dataLoader';
import storage from './services/storage';
import { getRecommendedPracticeWords, getRecommendedPracticeNouns, getSRSStatisticsForLevel } from './services/collocation';
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

  // JLPT Level selection
  const [jlptLevel, setJlptLevel] = useState(() => {
    // Load from localStorage on initial mount
    return localStorage.getItem('jlptLevel') || null;
  });
  const [studyListWords, setStudyListWords] = useState(new Set());
  const [srsStats, setSrsStats] = useState(null);

  // Navigation state
  const [currentScreen, setCurrentScreen] = useState('home'); // home, game-setup, playing
  const [gameConfig, setGameConfig] = useState(null);
  const [currentWord, setCurrentWord] = useState(null);
  const [wordQueue, setWordQueue] = useState([]);

  // Reset dialog state
  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  // Load study list and SRS statistics when JLPT level changes
  useEffect(() => {
    const loadStudyListAndStats = async () => {
      if (!jlptLevel) {
        setStudyListWords(new Set());
        setSrsStats(null);
        return;
      }

      try {
        const filename = jlptLevel === 'n5' ? 'studylist_n5.json' : 'studylist_n54.json';
        const response = await fetch(`${import.meta.env.BASE_URL}data/${filename}`);
        if (!response.ok) {
          throw new Error(`Failed to load study list: ${response.statusText}`);
        }
        const data = await response.json();
        const wordsSet = new Set(data.words);
        setStudyListWords(wordsSet);
        console.log(`Loaded ${data.words.length} words for ${jlptLevel.toUpperCase()}`);

        // Load SRS statistics for this level
        const stats = await getSRSStatisticsForLevel(jlptLevel, wordsSet);
        setSrsStats(stats);
      } catch (err) {
        console.error('Error loading study list:', err);
        setError(`Failed to load study list: ${err.message}`);
      }
    };

    loadStudyListAndStats();
  }, [jlptLevel]);

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

  const handleJlptLevelSelect = (level) => {
    setJlptLevel(level);
    localStorage.setItem('jlptLevel', level);
    setError(null); // Clear any errors
  };

  const handleStartGame = async (config) => {
    setGameConfig(config);
    setError(null); // Clear any previous errors

    // Get word queue based on mode
    let queue = [];
    let wordType;
    let isReverseMode = false;

    // Determine word type and mode based on config
    if (config.mode === 'verb-to-noun') {
      wordType = 'verb';
      isReverseMode = false;
    } else if (config.mode === 'adjective-to-noun') {
      wordType = 'adjective';
      isReverseMode = false;
    } else if (config.mode === 'noun-to-verb' || config.mode === 'noun-to-adjective') {
      wordType = 'noun';
      isReverseMode = true;
    }

    try {
      let recommended;

      // Use different function for reverse modes (noun-to-verb, noun-to-adjective)
      if (isReverseMode) {
        recommended = await getRecommendedPracticeNouns(10);
      } else {
        recommended = await getRecommendedPracticeWords(10);
      }

      // Filter by word type AND study list
      queue = recommended
        .filter(c => c.type === wordType && studyListWords.has(c.word || c.japanese))
        .map(c => ({
          id: c.word || c.japanese,
          japanese: c.word || c.japanese,
          reading: c.reading,
          english: c.english,
          type: c.type,
        }));

      if (queue.length === 0) {
        setError(`No ${wordType}s available for practice in ${jlptLevel?.toUpperCase() || 'selected'} study list. Try a different game mode or JLPT level.`);
        // Stay on game-setup screen
        return;
      }

      setWordQueue(queue);
      setCurrentWord(queue[0]);
      setCurrentScreen('playing');
    } catch (err) {
      console.error('Error starting game:', err);
      setError(`Failed to start game: ${err.message}`);
      // Stay on game-setup screen
    }
  };

  const handleGameComplete = (results) => {
    console.log('Game results:', results);

    // Check if user wants to skip queue and return to menu
    if (results?.skipQueue) {
      console.log('[App] User requested back to menu');
      setCurrentScreen('game-setup');
      setWordQueue([]);
      setCurrentWord(null);
      return;
    }

    console.log('[App] Current word queue:', wordQueue.map(w => w.japanese));
    console.log('[App] Current word:', currentWord?.japanese);

    // Move to next word in queue
    const currentIndex = wordQueue.findIndex(w => w.japanese === currentWord.japanese);
    console.log('[App] Current word index:', currentIndex, 'Queue length:', wordQueue.length);

    if (currentIndex !== -1 && currentIndex < wordQueue.length - 1) {
      // There's a next word
      const nextWord = wordQueue[currentIndex + 1];
      console.log('[App] Moving to next word:', nextWord.japanese);
      setCurrentWord(nextWord);
    } else {
      // No more words - return to setup
      console.log('[App] No more words, returning to game-setup');
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
    setError(null); // Clear any errors when going home
  };

  const handleResetClick = () => {
    setResetDialogOpen(true);
  };

  const handleResetCancel = () => {
    setResetDialogOpen(false);
  };

  const handleResetConfirm = async () => {
    try {
      await storage.clearAllData();
      setResetDialogOpen(false);
      setError(null);
      // Show success by reloading stats
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
      // Reload SRS statistics for current level
      if (jlptLevel && studyListWords.size > 0) {
        const srsStats = await getSRSStatisticsForLevel(jlptLevel, studyListWords);
        setSrsStats(srsStats);
      }
    } catch (err) {
      console.error('Error resetting SRS history:', err);
      setError(`Failed to reset SRS history: ${err.message}`);
      setResetDialogOpen(false);
    }
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

  if (error && !initialized) {
    // Only show full-screen error if initialization failed
    return (
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button variant="contained" onClick={() => window.location.reload()}>
            Reload Page
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
          {jlptLevel && (
            <Chip
              label={jlptLevel === 'n5' ? 'N5' : 'N5+N4'}
              color="primary"
              size="small"
              sx={{ mr: 2 }}
            />
          )}
          {currentScreen === 'playing' && wordQueue.length > 0 && currentWord && (
            <Typography variant="body2">
              Word {wordQueue.findIndex(w => w.japanese === currentWord.japanese) + 1} / {wordQueue.length}
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
              <Typography variant="h5" gutterBottom align="center">
                Select Your Study Level
              </Typography>
              <Typography variant="body1" paragraph align="center" color="text.secondary">
                Choose which JLPT vocabulary level you want to practice
              </Typography>

              <Box sx={{ mt: 3, mb: 4, display: 'flex', gap: 2, justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
                <ButtonGroup size="large" variant="outlined" sx={{ width: '100%', maxWidth: 400 }}>
                  <Button
                    onClick={() => handleJlptLevelSelect('n5')}
                    variant={jlptLevel === 'n5' ? 'contained' : 'outlined'}
                    startIcon={jlptLevel === 'n5' ? <CheckIcon /> : null}
                    sx={{ flex: 1, flexDirection: 'column', py: 1.5 }}
                  >
                    <Typography variant="button" sx={{ display: 'block' }}>N5</Typography>
                    <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem', mt: 0.5 }}>
                      (703 words)
                    </Typography>
                  </Button>
                  <Button
                    onClick={() => handleJlptLevelSelect('n54')}
                    variant={jlptLevel === 'n54' ? 'contained' : 'outlined'}
                    startIcon={jlptLevel === 'n54' ? <CheckIcon /> : null}
                    sx={{ flex: 1, flexDirection: 'column', py: 1.5 }}
                  >
                    <Typography variant="button" sx={{ display: 'block' }}>N5 + N4</Typography>
                    <Typography variant="caption" sx={{ display: 'block', fontSize: '0.7rem', mt: 0.5 }}>
                      (1342 words)
                    </Typography>
                  </Button>
                </ButtonGroup>

                {!jlptLevel && (
                  <Alert severity="info" sx={{ mt: 2, maxWidth: 400 }}>
                    Please select a study level to continue
                  </Alert>
                )}
              </Box>

              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<GameIcon />}
                  onClick={() => setCurrentScreen('game-setup')}
                  disabled={!jlptLevel}
                >
                  Start Playing
                </Button>
              </Box>
            </Paper>

            {/* SRS Statistics for Selected Level */}
            {jlptLevel && srsStats && (
              <Box sx={{ mt: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUpIcon sx={{ mr: 1 }} color="primary" />
                  <Typography variant="h6">
                    Your Progress - {jlptLevel === 'n5' ? 'N5' : 'N5+N4'}
                  </Typography>
                </Box>

                {/* Overall Progress */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ bgcolor: 'primary.main', color: 'primary.contrastText' }}>
                      <CardContent>
                        <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                          Words Practiced
                        </Typography>
                        <Typography variant="h3">
                          {srsStats.practiced} / {srsStats.total}
                        </Typography>
                        <Typography variant="h6" sx={{ mt: 1 }}>
                          {srsStats.practicedPercentage}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Card sx={{ bgcolor: 'success.main', color: 'success.contrastText' }}>
                      <CardContent>
                        <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                          Mastery Level
                        </Typography>
                        <Typography variant="h3">
                          {srsStats.young + srsStats.mature + srsStats.mastered}
                        </Typography>
                        <Typography variant="h6" sx={{ mt: 1 }}>
                          {srsStats.masteryPercentage}% mastered
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* SRS Maturity Breakdown */}
                <Typography variant="subtitle1" gutterBottom sx={{ mt: 3, mb: 1, display: 'flex', alignItems: 'center' }}>
                  <SchoolIcon sx={{ mr: 1, fontSize: '1.2rem' }} />
                  Learning Progress
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={2.4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          New
                        </Typography>
                        <Typography variant="h4">
                          {srsStats.new}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Not practiced
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={2.4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Learning
                        </Typography>
                        <Typography variant="h4">
                          {srsStats.learning}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          &lt;3 correct
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={2.4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Young
                        </Typography>
                        <Typography variant="h4">
                          {srsStats.young}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          3-5 correct
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={2.4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Mature
                        </Typography>
                        <Typography variant="h4">
                          {srsStats.mature}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          6-10 correct
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={2.4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Mastered
                        </Typography>
                        <Typography variant="h4">
                          {srsStats.mastered}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          &gt;10 correct
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Word Type Breakdown */}
                <Typography variant="subtitle1" gutterBottom sx={{ mt: 3, mb: 1 }}>
                  By Word Type
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Nouns
                        </Typography>
                        <Typography variant="h5">
                          {srsStats.byType.noun.practiced} / {srsStats.byType.noun.total}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {srsStats.byType.noun.total > 0
                            ? Math.round((srsStats.byType.noun.practiced / srsStats.byType.noun.total) * 100)
                            : 0}% practiced
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Verbs
                        </Typography>
                        <Typography variant="h5">
                          {srsStats.byType.verb.practiced} / {srsStats.byType.verb.total}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {srsStats.byType.verb.total > 0
                            ? Math.round((srsStats.byType.verb.practiced / srsStats.byType.verb.total) * 100)
                            : 0}% practiced
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={4}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography color="text.secondary" gutterBottom variant="body2">
                          Adjectives
                        </Typography>
                        <Typography variant="h5">
                          {srsStats.byType.adjective.practiced} / {srsStats.byType.adjective.total}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {srsStats.byType.adjective.total > 0
                            ? Math.round((srsStats.byType.adjective.practiced / srsStats.byType.adjective.total) * 100)
                            : 0}% practiced
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}

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

            <Box sx={{ mt: 4, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="caption" display="block" color="text.secondary" align="center">
                100% Serverless - All data stored in your browser
              </Typography>
              <Typography variant="caption" display="block" color="text.secondary" align="center">
                Your progress persists across sessions (even when browser is shut down)
              </Typography>
            </Box>

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<DeleteIcon />}
                onClick={handleResetClick}
              >
                Reset All Progress
              </Button>
            </Box>
          </Box>
        )}

        {currentScreen === 'game-setup' && (
          <Box>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            <GameModeSelector onStartGame={handleStartGame} />
          </Box>
        )}

        {currentScreen === 'playing' && currentWord && gameConfig && (
          <WhatCouldMatch
            key={currentWord.japanese}
            word={currentWord}
            onComplete={handleGameComplete}
            mode={gameConfig.mode}
            matchCount={gameConfig.matchCount}
            newWordsTarget={gameConfig.newWordsTarget}
            studyListWords={studyListWords}
          />
        )}
      </Container>

      {/* Reset Confirmation Dialog */}
      <Dialog
        open={resetDialogOpen}
        onClose={handleResetCancel}
        aria-labelledby="reset-dialog-title"
        aria-describedby="reset-dialog-description"
      >
        <DialogTitle id="reset-dialog-title">
          Reset All Progress?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="reset-dialog-description">
            This will permanently delete all your learning progress, including:
            <br />
            • All word practice history
            <br />
            • All collocation practice history
            <br />
            • All SRS (spaced repetition) data
            <br />
            <br />
            This action cannot be undone. Are you sure you want to continue?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleResetCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleResetConfirm} color="error" variant="contained" startIcon={<DeleteIcon />}>
            Reset All Progress
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default App;
