/**
 * What Could Match Game Component
 *
 * Game where user finds all words that match with a given word.
 * Example: "What can you drink?" → water, coffee, beer, etc.
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  EmojiEvents as TrophyIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import PropTypes from 'prop-types';
import FuriganaText from '../ui/FuriganaText';
import AnswerInput from '../ui/AnswerInput';
import { getCollocation } from '../../services/collocation';
import { recordReview } from '../../services/srs';
import { CollocationProgress } from '../../models/Progress';
import storage from '../../services/storage';

function WhatCouldMatch({ word, onComplete, mode = 'verb-to-noun' }) {
  const [collocation, setCollocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gameState, setGameState] = useState('playing'); // playing, finished
  const [answers, setAnswers] = useState([]);
  const [foundMatches, setFoundMatches] = useState(new Set());
  const [totalMatches, setTotalMatches] = useState(0);
  const [score, setScore] = useState(0);

  useEffect(() => {
    // Reset state when word changes
    setLoading(true);
    setError(null);
    setGameState('playing');
    setAnswers([]);
    setFoundMatches(new Set());
    setScore(0);

    const loadWord = async () => {
      try {
        const data = await getCollocation(word.japanese);
        if (data) {
          setCollocation(data);
          const matches = data.getNounMatches();
          setTotalMatches(matches.length);

          if (matches.length === 0) {
            setError('No collocation data available for this word.');
          }
        } else {
          setError('Failed to load collocation data for this word.');
        }
      } catch (err) {
        console.error('Error loading collocation:', err);
        setError(`Error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadWord();
  }, [word.japanese]); // Only depend on word.japanese to avoid infinite loop

  const handleAnswer = async (answer) => {
    if (!collocation || gameState !== 'playing') return;

    const matches = collocation.getNounMatches();
    const match = matches.find(m => m.word === answer);

    const isCorrect = !!match;
    const alreadyFound = foundMatches.has(answer);

    const newAnswer = {
      answer,
      correct: isCorrect,
      score: match ? match.score : 0,
      reading: match ? match.reading : '',
      english: match ? match.english : '',
      duplicate: isCorrect && alreadyFound,
    };

    setAnswers([...answers, newAnswer]);

    // Only process if it's a new correct answer or a wrong answer
    if (isCorrect && !alreadyFound) {
      // New correct answer
      const newFoundMatches = new Set(foundMatches);
      newFoundMatches.add(answer);
      setFoundMatches(newFoundMatches);
      setScore(score + match.score);

      // Save collocation progress
      const pairId = `${word.japanese}|${answer}`;
      const progress = await storage.getCollocationProgress(pairId);
      const collocationProgress = new CollocationProgress(progress || { pairId });
      collocationProgress.recordCorrect();
      await storage.saveCollocationProgress(pairId, collocationProgress.toJSON());
    } else if (!isCorrect) {
      // Wrong answer (not a valid match)
      const pairId = `${word.japanese}|${answer}`;
      const progress = await storage.getCollocationProgress(pairId);
      const collocationProgress = new CollocationProgress(progress || { pairId });
      collocationProgress.recordIncorrect();
      await storage.saveCollocationProgress(pairId, collocationProgress.toJSON());
    }
    // If duplicate correct answer, just ignore (don't record as incorrect)
  };

  const handleGiveUp = async () => {
    // Calculate performance for SRS
    const foundCount = foundMatches.size;
    const percentage = totalMatches > 0 ? (foundCount / totalMatches) * 100 : 0;

    let srsAnswer = 'again';
    if (percentage >= 90) srsAnswer = 'easy';
    else if (percentage >= 70) srsAnswer = 'good';
    else if (percentage >= 40) srsAnswer = 'hard';

    // Record review for this word
    await recordReview(word.id, srsAnswer);

    setGameState('finished');
  };

  const handleContinue = () => {
    if (onComplete) {
      onComplete({
        word: word.japanese,
        foundMatches: foundMatches.size,
        totalMatches,
        score,
        answers,
      });
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 4 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }} align="center">Loading word...</Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Typography variant="body2" color="text.secondary" paragraph>
          Word: {word.japanese} ({word.reading})
        </Typography>
        <Button
          variant="contained"
          startIcon={<HomeIcon />}
          onClick={() => onComplete && onComplete({ error: true })}
        >
          Skip This Word
        </Button>
      </Paper>
    );
  }

  const progress = totalMatches > 0 ? (foundMatches.size / totalMatches) * 100 : 0;
  const allMatches = collocation.getNounMatches();
  const missedMatches = allMatches.filter(m => !foundMatches.has(m.word));

  return (
    <Paper sx={{ p: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom align="center">
          {mode === 'verb-to-noun' ? 'What could match?' : 'Find all matches!'}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center">
          {mode === 'verb-to-noun'
            ? `Find all nouns that can pair with this ${word.type}`
            : 'Find all words that match'}
        </Typography>
      </Box>

      {/* Word Display */}
      <FuriganaText
        japanese={word.japanese}
        reading={word.reading}
        english={word.english}
        showEnglish={false}
        size="xlarge"
      />

      {/* Progress */}
      <Box sx={{ my: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2">
            Found: {foundMatches.size} / {totalMatches}
          </Typography>
          <Typography variant="body2" color="primary">
            Score: {score}
          </Typography>
        </Box>
        <LinearProgress variant="determinate" value={progress} />
      </Box>

      {gameState === 'playing' ? (
        <>
          {/* Answer Input */}
          <Box sx={{ mb: 3 }}>
            <AnswerInput
              onSubmit={handleAnswer}
              previousAnswers={answers.slice(-5)}
              placeholder="Type a Japanese word..."
            />
          </Box>

          {/* Give Up Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="outlined"
              color="error"
              onClick={handleGiveUp}
            >
              Give Up / Show Answers
            </Button>
          </Box>
        </>
      ) : (
        <>
          {/* Results */}
          <Alert
            severity={progress >= 70 ? 'success' : progress >= 40 ? 'warning' : 'error'}
            icon={progress >= 70 ? <TrophyIcon /> : undefined}
            sx={{ mb: 3 }}
          >
            You found {foundMatches.size} out of {totalMatches} matches ({Math.round(progress)}%)!
            Score: {score} points
          </Alert>

          {/* Found Matches */}
          {foundMatches.size > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckIcon color="success" />
                Correct Answers ({foundMatches.size})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {allMatches
                  .filter(m => foundMatches.has(m.word))
                  .map((match, idx) => (
                    <Chip
                      key={idx}
                      label={`${match.word} (${match.reading}) - ${match.english}`}
                      color="success"
                      variant="outlined"
                    />
                  ))}
              </Box>
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* Missed Matches */}
          {missedMatches.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CancelIcon color="error" />
                Missed Answers ({missedMatches.length})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {missedMatches.map((match, idx) => (
                  <Chip
                    key={idx}
                    label={`${match.word} (${match.reading}) - ${match.english}`}
                    color="error"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Continue Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleContinue}
            >
              Continue
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
}

WhatCouldMatch.propTypes = {
  word: PropTypes.shape({
    id: PropTypes.string.isRequired,
    japanese: PropTypes.string.isRequired,
    reading: PropTypes.string.isRequired,
    english: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
  }).isRequired,
  onComplete: PropTypes.func,
  mode: PropTypes.string,
};

export default WhatCouldMatch;
