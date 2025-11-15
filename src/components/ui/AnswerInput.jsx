/**
 * Answer Input Component
 *
 * Text input field for Japanese answers with submit handling.
 * Includes IME-style candidate selection.
 */

import { useState, useRef, useEffect } from 'react';
import { TextField, Button, Box, Chip, Paper, List, ListItem, ListItemText } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import PropTypes from 'prop-types';

function AnswerInput({ onSubmit, disabled = false, placeholder = 'Enter your answer in Japanese...', previousAnswers = [], availableWords = [] }) {
  const [answer, setAnswer] = useState('');
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidateIndex, setSelectedCandidateIndex] = useState(0);
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus input when enabled
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled, previousAnswers]);

  // Find candidates based on input (match kanji directly)
  const findCandidates = (input) => {
    if (!input || availableWords.length === 0) {
      return [];
    }

    // Find all words where the word/kanji matches the input
    const matches = availableWords.filter(word => {
      return word.word === input || word.word.startsWith(input);
    });

    // Sort by exact match first, then by word length
    matches.sort((a, b) => {
      if (a.word === input && b.word !== input) return -1;
      if (a.word !== input && b.word === input) return 1;
      return a.word.length - b.word.length;
    });

    return matches;
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedAnswer = answer.trim();

    if (trimmedAnswer && !disabled) {
      onSubmit(trimmedAnswer);
      setAnswer('');
      setCandidates([]);
      setSelectedCandidateIndex(0);
    }
  };

  const handleKeyDown = (e) => {
    // Handle spacebar for candidate selection
    if (e.key === ' ') {
      if (candidates.length > 0) {
        // Already showing candidates: cycle through them
        e.preventDefault();
        const nextIndex = (selectedCandidateIndex + 1) % candidates.length;
        setSelectedCandidateIndex(nextIndex);
        setAnswer(candidates[nextIndex].word);
      } else {
        // Not showing candidates yet: check if we can show them
        const currentValue = answer.trim();

        if (currentValue.length > 0) {
          const matches = findCandidates(currentValue);

          if (matches.length > 0) {
            // Prevent default only if we have candidates to show
            e.preventDefault();
            setCandidates(matches);
            setSelectedCandidateIndex(0);
            // Replace input with first candidate
            setAnswer(matches[0].word);
          }
          // If no matches, let spacebar add space normally
        }
      }
    }
    // Handle Enter for submission
    else if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
    // Handle Escape to cancel candidate selection
    else if (e.key === 'Escape') {
      setCandidates([]);
      setSelectedCandidateIndex(0);
    }
  };

  // Update candidates when answer changes (typing)
  const handleChange = (e) => {
    const newValue = e.target.value;
    setAnswer(newValue);

    // Clear candidates when user starts typing again
    if (candidates.length > 0) {
      setCandidates([]);
      setSelectedCandidateIndex(0);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {previousAnswers.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {previousAnswers.map((ans, idx) => {
            // Determine chip color and label
            let chipColor = 'error';
            let chipLabel = ans.answer;

            if (ans.correct) {
              if (ans.isBonus) {
                chipColor = 'warning'; // Orange for bonus
                chipLabel = `${ans.answer} (bonus)`;
              } else {
                chipColor = 'success'; // Green for target
              }
            }

            return (
              <Chip
                key={idx}
                label={chipLabel}
                color={chipColor}
                size="small"
                variant="outlined"
              />
            );
          })}
        </Box>
      )}

      <Box sx={{ position: 'relative' }}>
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}
        >
          <TextField
            inputRef={inputRef}
            fullWidth
            value={answer}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            variant="outlined"
            autoComplete="off"
            inputProps={{
              style: {
                fontSize: '1.2rem',
                fontFamily: 'Noto Sans JP, sans-serif',
              },
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                fontSize: '1.2rem',
              },
            }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={disabled || !answer.trim()}
            endIcon={<SendIcon />}
            sx={{ minWidth: '100px', height: '56px' }}
          >
            Submit
          </Button>
        </Box>

        {/* IME Candidate List */}
        {candidates.length > 0 && (
          <Paper
            elevation={3}
            sx={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 100,
              mt: 0.5,
              maxHeight: '200px',
              overflow: 'auto',
              zIndex: 1000,
            }}
          >
            <List dense>
              {candidates.map((candidate, index) => (
                <ListItem
                  key={index}
                  selected={index === selectedCandidateIndex}
                  sx={{
                    backgroundColor: index === selectedCandidateIndex ? 'primary.light' : 'transparent',
                    '&:hover': {
                      backgroundColor: index === selectedCandidateIndex ? 'primary.light' : 'action.hover',
                    },
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <span style={{ fontFamily: 'Noto Sans JP, sans-serif', fontSize: '1.1rem' }}>
                          {candidate.word}
                        </span>
                        <span style={{ color: 'text.secondary', fontSize: '0.9rem' }}>
                          ({candidate.reading})
                        </span>
                      </Box>
                    }
                    secondary={candidate.english}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}
      </Box>
    </Box>
  );
}

AnswerInput.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
  placeholder: PropTypes.string,
  previousAnswers: PropTypes.arrayOf(
    PropTypes.shape({
      answer: PropTypes.string.isRequired,
      correct: PropTypes.bool.isRequired,
      isBonus: PropTypes.bool,
    })
  ),
  availableWords: PropTypes.arrayOf(
    PropTypes.shape({
      word: PropTypes.string.isRequired,
      reading: PropTypes.string.isRequired,
      english: PropTypes.string.isRequired,
    })
  ),
};

export default AnswerInput;
