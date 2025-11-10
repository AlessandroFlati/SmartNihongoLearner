/**
 * Game Mode Selector Component
 *
 * Allows user to start a game and select practice words.
 */

import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Alert,
} from '@mui/material';
import { PlayArrow as PlayIcon } from '@mui/icons-material';
import PropTypes from 'prop-types';

function GameModeSelector({ onStartGame }) {
  const [mode, setMode] = useState('verb-to-noun');
  const [wordSelection, setWordSelection] = useState('recommended');

  const handleStart = () => {
    onStartGame({
      mode,
      wordSelection,
    });
  };

  return (
    <Paper sx={{ p: 4, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom align="center">
        What Could Match Game
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph align="center">
        Find all words that match with the given word
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        In this game, you'll be given a Japanese word (verb or adjective), and you need to find
        all the nouns that naturally pair with it. For example, for のむ (to drink), you'd enter
        words like 水 (water), コーヒー (coffee), etc.
      </Alert>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Game Mode
        </Typography>
        <FormControl component="fieldset" fullWidth>
          <RadioGroup value={mode} onChange={(e) => setMode(e.target.value)}>
            <FormControlLabel
              value="verb-to-noun"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Verb → Nouns</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Given a verb, find all matching nouns (e.g., "What can you drink?")
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="adjective-to-noun"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Adjective → Nouns</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Given an adjective, find all matching nouns (e.g., "What can be delicious?")
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Word Selection
        </Typography>
        <FormControl component="fieldset" fullWidth>
          <RadioGroup value={wordSelection} onChange={(e) => setWordSelection(e.target.value)}>
            <FormControlLabel
              value="recommended"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Recommended</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Words you haven't practiced much, prioritized by difficulty
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="random"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Random</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Any random word from the vocabulary list
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="due"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Due for Review</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Words scheduled for review based on SRS algorithm
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<PlayIcon />}
          onClick={handleStart}
        >
          Start Game
        </Button>
      </Box>
    </Paper>
  );
}

GameModeSelector.propTypes = {
  onStartGame: PropTypes.func.isRequired,
};

export default GameModeSelector;
