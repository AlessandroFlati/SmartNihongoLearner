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
  Slider,
} from '@mui/material';
import { PlayArrow as PlayIcon } from '@mui/icons-material';
import PropTypes from 'prop-types';

function GameModeSelector({ onStartGame }) {
  const [mode, setMode] = useState('verb-to-noun');
  const [matchCount, setMatchCount] = useState(10);
  const [newWordsTarget, setNewWordsTarget] = useState(5);

  const handleStart = () => {
    onStartGame({
      mode,
      matchCount,
      newWordsTarget,
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
        Find all words that naturally pair together in Japanese. Match verbs with nouns,
        adjectives with nouns, or find which verbs/adjectives can describe a given noun.
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
            <FormControlLabel
              value="noun-to-verb"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Noun → Verbs</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Given a noun, find all verbs that pair with it (e.g., "What can you do with water?")
                  </Typography>
                </Box>
              }
            />
            <FormControlLabel
              value="noun-to-adjective"
              control={<Radio />}
              label={
                <Box>
                  <Typography variant="body1">Noun → Adjectives</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Given a noun, find all adjectives that describe it (e.g., "How can food be?")
                  </Typography>
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Total Matches Per Word
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          How many matches to find for each word
        </Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={matchCount}
            onChange={(e, newValue) => {
              setMatchCount(newValue);
              // Auto-adjust newWordsTarget to half when matchCount changes
              const newTarget = Math.floor(newValue / 2);
              if (newWordsTarget > newValue) {
                setNewWordsTarget(newValue);
              } else {
                setNewWordsTarget(newTarget);
              }
            }}
            min={5}
            max={20}
            step={1}
            marks={[
              { value: 5, label: '5' },
              { value: 10, label: '10' },
              { value: 15, label: '15' },
              { value: 20, label: '20' },
            ]}
            valueLabelDisplay="on"
          />
        </Box>
      </Box>

      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          New Words Target
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          How many should be NEW (never practiced). Remaining will be REVIEW (weak/struggling)
        </Typography>
        <Box sx={{ px: 2 }}>
          <Slider
            value={newWordsTarget}
            onChange={(e, newValue) => setNewWordsTarget(newValue)}
            min={0}
            max={matchCount}
            step={1}
            marks={[
              { value: 0, label: '0' },
              { value: Math.floor(matchCount * 0.25), label: `${Math.floor(matchCount * 0.25)}` },
              { value: Math.floor(matchCount * 0.5), label: `${Math.floor(matchCount * 0.5)}` },
              { value: Math.floor(matchCount * 0.75), label: `${Math.floor(matchCount * 0.75)}` },
              { value: matchCount, label: `${matchCount}` },
            ]}
            valueLabelDisplay="on"
          />
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, textAlign: 'center' }}>
          New: {newWordsTarget} | Review: {matchCount - newWordsTarget}
        </Typography>
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
