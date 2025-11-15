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
import { getCollocation, getLimitedNounMatchesWithProgress, getReverseCollocation } from '../../services/collocation';
import { recordReview } from '../../services/srs';
import { CollocationProgress } from '../../models/Progress';
import storage from '../../services/storage';
import { getHintsForWord } from '../../services/dataLoader';
import * as wanakana from 'wanakana';

function WhatCouldMatch({ word, onComplete, mode = 'verb-to-noun', matchCount = 15, newWordsTarget = 3, studyListWords = new Set() }) {
  const [collocation, setCollocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gameState, setGameState] = useState('playing'); // playing, finished
  const [answers, setAnswers] = useState([]);
  const [foundMatches, setFoundMatches] = useState(new Set());
  const [bonusMatches, setBonusMatches] = useState(new Set()); // Valid but not in target
  const [totalMatches, setTotalMatches] = useState(0);
  const [score, setScore] = useState(0);
  const [limitedMatches, setLimitedMatches] = useState([]);
  const [bonusWarningCount, setBonusWarningCount] = useState(0);
  const [currentHintIndex, setCurrentHintIndex] = useState(0); // Index of current word being hinted
  const [skippedWords, setSkippedWords] = useState(new Set()); // Words user couldn't remember
  const [wordHints, setWordHints] = useState({}); // Semantic hints for each noun

  // Helper function to get matches based on mode
  const getMatchesForMode = (collocationObj) => {
    if (!collocationObj) return [];

    switch (mode) {
      case 'verb-to-noun':
      case 'adjective-to-noun':
        return collocationObj.getNounMatches();
      case 'noun-to-verb':
        return collocationObj.getVerbMatches();
      case 'noun-to-adjective':
        return collocationObj.getAdjectiveMatches();
      default:
        return [];
    }
  };

  useEffect(() => {
    // Reset state when word changes
    setLoading(true);
    setError(null);
    setGameState('playing');
    setAnswers([]);
    setFoundMatches(new Set());
    setBonusMatches(new Set());
    setScore(0);
    setLimitedMatches([]);
    setBonusWarningCount(0);
    setCurrentHintIndex(0);
    setSkippedWords(new Set());
    setWordHints({});

    const loadWord = async () => {
      try {
        let data;

        // Load collocation or reverse collocation based on mode
        if (mode === 'noun-to-verb' || mode === 'noun-to-adjective') {
          // Reverse mode: noun looking for verbs/adjectives
          data = await getReverseCollocation(word.japanese, word);
        } else {
          // Forward mode: verb/adjective looking for nouns
          data = await getCollocation(word.japanese);
        }

        if (data) {
          setCollocation(data);

          // Get all matches for this mode
          const allMatches = getMatchesForMode(data);

          // Filter matches by study list (if provided)
          const filteredMatches = studyListWords.size > 0
            ? allMatches.filter(m => studyListWords.has(m.word))
            : allMatches;


          // For noun-to-verb/adjective modes, use simple top N selection
          // For verb/adjective-to-noun modes, use SRS-based selection
          let matches;
          if (mode === 'noun-to-verb' || mode === 'noun-to-adjective') {
            // Simple selection: take top N by score from filtered matches
            matches = filteredMatches.slice(0, matchCount);
          } else {
            // SRS-based selection from filtered matches
            matches = await getLimitedNounMatchesWithProgress(word.japanese, data, matchCount, newWordsTarget, filteredMatches);
          }

          setLimitedMatches(matches);
          setTotalMatches(matches.length);

          // Load hints for this word
          const hintMode = (mode === 'noun-to-verb' || mode === 'noun-to-adjective') ? 'reverse' : 'forward';
          const hints = await getHintsForWord(word.japanese, hintMode);
          setWordHints(hints);

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
  }, [word.japanese, matchCount, newWordsTarget, mode]); // Depend on word, matchCount, newWordsTarget, and mode

  const handleAnswer = async (answer) => {
    if (!collocation || gameState !== 'playing') return;

    // Convert answer to romaji if it's kana (readings in DB are romaji)
    const answerRomaji = wanakana.isKana(answer) ? wanakana.toRomaji(answer) : answer;


    // Check for duplicate readings in target matches
    const duplicateReadings = limitedMatches.filter(m => m.reading === answerRomaji);
    if (duplicateReadings.length > 1) {
      console.warn('[WhatCouldMatch] Multiple words with same reading:',
        duplicateReadings.map(m => `${m.word}(${m.reading})`).join(', '));
    }

    // IMPORTANT: Search TARGET matches first to avoid homophone collisions
    // Example: うち could match both 家 (house) and 中 (inside)
    // Strategy:
    // 1. First check for exact kanji match (highest priority)
    // 2. Then check for reading match, but prioritize words NOT already found
    //    (this allows finding all words even if they share the same reading)

    // Try exact kanji match first
    let match = limitedMatches.find(m => m.word === answer);

    // If no exact match, try reading match - prioritize unfound words
    if (!match) {
      // First try to find unfound word with this reading
      match = limitedMatches.find(m =>
        m.reading === answerRomaji && !foundMatches.has(m.word)
      );

      // If all words with this reading are already found, match any (will be marked duplicate)
      if (!match) {
        match = limitedMatches.find(m => m.reading === answerRomaji);
      }
    }


    // Only if not found in target matches, check bonus matches
    if (!match) {
      const allMatches = getMatchesForMode(collocation);

      // Try exact kanji match first
      match = allMatches.find(m => m.word === answer);

      // If no exact match, try reading match - prioritize unfound words
      if (!match) {
        // First try to find unfound word with this reading
        match = allMatches.find(m =>
          m.reading === answerRomaji && !bonusMatches.has(m.word) && !foundMatches.has(m.word)
        );

        // If all words with this reading are already found, match any (will be marked duplicate)
        if (!match) {
          match = allMatches.find(m => m.reading === answerRomaji);
        }
      }

    }

    const isCorrect = !!match;

    // Normalize answer to kanji form for consistent tracking
    const normalizedAnswer = match ? match.word : answer;

    const isTargetMatch = limitedMatches.some(m => m.word === normalizedAnswer);
    const alreadyFoundTarget = foundMatches.has(normalizedAnswer);
    const alreadyFoundBonus = bonusMatches.has(normalizedAnswer);
    const alreadyFound = alreadyFoundTarget || alreadyFoundBonus;

    const isBonus = isCorrect && !isTargetMatch;

    const newAnswer = {
      answer,
      correct: isCorrect,
      isBonus,
      score: match ? match.score : 0,
      points: isBonus ? 0 : (match ? match.score : 0), // Zero points for bonus
      reading: match ? match.reading : '',
      english: match ? match.english : '',
      duplicate: isCorrect && alreadyFound,
    };

    setAnswers([...answers, newAnswer]);

    // Only process if it's a new correct answer or a wrong answer
    if (isCorrect && !alreadyFound) {
      if (isTargetMatch) {
        // New TARGET match found
        const newFoundMatches = new Set(foundMatches);
        newFoundMatches.add(normalizedAnswer);
        setFoundMatches(newFoundMatches);
        setScore(score + match.score);

        // Move to next hint
        setCurrentHintIndex(currentHintIndex + 1);


        // Check if all words have been found OR all words accounted for (found + skipped)
        if (newFoundMatches.size + skippedWords.size === totalMatches) {
          // Game complete! Either all found, or combination of found + skipped
          setTimeout(async () => {
            // Calculate SRS based on how many were skipped
            const skippedCount = skippedWords.size;
            const foundCount = newFoundMatches.size;
            const percentage = (foundCount / (foundCount + skippedCount)) * 100;

            let srsAnswer = 'good';
            if (percentage >= 90) srsAnswer = 'easy';
            else if (percentage >= 70) srsAnswer = 'good';
            else if (percentage >= 50) srsAnswer = 'hard';
            else srsAnswer = 'again';

            await recordReview(word.id, srsAnswer);
            setGameState('finished');
          }, 500); // Small delay to let the UI update
        }
      } else {
        // New BONUS match found (valid but not in target)
        const newBonusMatches = new Set(bonusMatches);
        newBonusMatches.add(normalizedAnswer);
        setBonusMatches(newBonusMatches);
        // Increment bonus warning counter
        setBonusWarningCount(bonusWarningCount + 1);
      }

      // Save collocation progress (for both target and bonus)
      const pairId = `${word.japanese}|${normalizedAnswer}`;
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

  const handleContinue = () => {
    if (onComplete) {
      onComplete({
        word: word.japanese,
        foundMatches: foundMatches.size,
        totalMatches,
        score,
        answers,
      });
    } else {
      console.error('[WhatCouldMatch] onComplete callback is missing!');
    }
  };

  const handleCantRemember = async () => {
    // Get unfound matches to skip
    const unfoundMatches = limitedMatches.filter(
      m => !foundMatches.has(m.word) && !skippedWords.has(m.word)
    );

    if (unfoundMatches.length === 0) return;

    // Get the current word (the one currently being hinted)
    const currentWord = unfoundMatches[0];

    // Mark as skipped
    const newSkippedWords = new Set(skippedWords);
    newSkippedWords.add(currentWord.word);
    setSkippedWords(newSkippedWords);

    // Record as incorrect for collocation progress
    const pairId = `${word.japanese}|${currentWord.word}`;
    const progress = await storage.getCollocationProgress(pairId);
    const collocationProgress = new CollocationProgress(progress || { pairId });
    collocationProgress.recordIncorrect();
    await storage.saveCollocationProgress(pairId, collocationProgress.toJSON());

    // Move to next word
    setCurrentHintIndex(currentHintIndex + 1);


    // Check if all words have been found or skipped
    if (foundMatches.size + newSkippedWords.size === totalMatches) {
      // Game over - calculate SRS based on performance
      setTimeout(async () => {
        const skippedCount = newSkippedWords.size;
        const foundCount = foundMatches.size;
        const percentage = (foundCount / (foundCount + skippedCount)) * 100;

        let srsAnswer = 'again';
        if (percentage >= 90) srsAnswer = 'easy';
        else if (percentage >= 70) srsAnswer = 'good';
        else if (percentage >= 50) srsAnswer = 'hard';

        await recordReview(word.id, srsAnswer);
        setGameState('finished');
      }, 500);
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

  // Use limited matches for display (only show the target matches)
  const limitedFoundMatches = limitedMatches.filter(m => foundMatches.has(m.word));
  const skippedMatches = limitedMatches.filter(m => skippedWords.has(m.word));
  const missedMatches = limitedMatches.filter(m => !foundMatches.has(m.word) && !skippedWords.has(m.word));
  const progress = totalMatches > 0 ? (limitedFoundMatches.length / totalMatches) * 100 : 0;

  // Get current word being hinted
  const unfoundMatches = limitedMatches.filter(
    m => !foundMatches.has(m.word) && !skippedWords.has(m.word)
  );
  const currentWord = unfoundMatches.length > 0 ? unfoundMatches[0] : null;
  const currentHint = currentWord ? wordHints[currentWord.word] : null;

  // Debug logging for hint display
  if (currentWord && gameState === 'playing') {
  }


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
            Found: {limitedFoundMatches.length} / {totalMatches}
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
              availableWords={collocation ? getMatchesForMode(collocation) : []}
            />
          </Box>

          {/* Bonus Warning Banner */}
          {bonusWarningCount >= 3 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              ⚠️ You're entering words you already know well. Try focusing on the target words you're learning!
              {bonusMatches.size > 0 && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Bonus words found: {bonusMatches.size} (tracked but no points)
                </Typography>
              )}
            </Alert>
          )}

          {/* Current Hint Display */}
          {currentHint && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>Current Word Hint:</Typography>
              <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                {currentHint}
              </Typography>
              {currentWord && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Word {foundMatches.size + skippedWords.size + 1} of {totalMatches}
                </Typography>
              )}
            </Alert>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              color="warning"
              onClick={handleCantRemember}
              disabled={!currentWord}
            >
              Can't Remember
            </Button>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => {
                if (onComplete) {
                  onComplete({ skipQueue: true });
                }
              }}
            >
              Back to Menu
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
            You found {limitedFoundMatches.length} out of {totalMatches} matches ({Math.round(progress)}%)!
            Score: {score} points
          </Alert>

          {/* Found Matches */}
          {/* Found Target Matches */}
          {limitedFoundMatches.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CheckIcon color="success" />
                Target Matches ({limitedFoundMatches.length})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {limitedMatches
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

          {/* Skipped Words (Can't Remember) */}
          {skippedMatches.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CancelIcon color="warning" />
                Words You Couldn't Remember ({skippedMatches.length})
              </Typography>
              {skippedMatches.map((match, idx) => {
                return (
                  <Alert key={idx} severity="warning" sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      {match.word} ({match.reading})
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {match.english}
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      <strong>Hint:</strong> {wordHints[match.word] || 'related item'}
                    </Typography>
                  </Alert>
                );
              })}
            </Box>
          )}

          {/* Missed Matches (Give Up) */}
          {missedMatches.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CancelIcon color="error" />
                Other Missed Answers ({missedMatches.length})
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

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 3 }}>
            <Button
              variant="outlined"
              size="large"
              onClick={() => {
                if (onComplete) {
                  onComplete({ skipQueue: true });
                } else {
                  console.error('[WhatCouldMatch] onComplete is missing for Back to Menu');
                }
              }}
            >
              Back to Menu
            </Button>
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
  matchCount: PropTypes.number,
  newWordsTarget: PropTypes.number,
  studyListWords: PropTypes.instanceOf(Set),
};

export default WhatCouldMatch;
