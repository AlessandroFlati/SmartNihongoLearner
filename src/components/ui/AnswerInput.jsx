/**
 * Answer Input Component
 *
 * Text input field for Japanese answers with submit handling.
 */

import { useState, useRef, useEffect } from 'react';
import { TextField, Button, Box, Chip } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import PropTypes from 'prop-types';

function AnswerInput({ onSubmit, disabled = false, placeholder = 'Enter your answer in Japanese...', previousAnswers = [] }) {
  const [answer, setAnswer] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    // Auto-focus input when enabled
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled, previousAnswers]);

  const handleSubmit = (e) => {
    e.preventDefault();

    const trimmedAnswer = answer.trim();
    if (trimmedAnswer && !disabled) {
      onSubmit(trimmedAnswer);
      setAnswer('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Box sx={{ width: '100%' }}>
      {previousAnswers.length > 0 && (
        <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {previousAnswers.map((ans, idx) => (
            <Chip
              key={idx}
              label={ans.answer}
              color={ans.correct ? 'success' : 'error'}
              size="small"
              variant="outlined"
            />
          ))}
        </Box>
      )}

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}
      >
        <TextField
          inputRef={inputRef}
          fullWidth
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
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

      <Box sx={{ mt: 1, display: 'flex', gap: 1, alignItems: 'center' }}>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setAnswer('を')}
          disabled={disabled}
        >
          を
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setAnswer('が')}
          disabled={disabled}
        >
          が
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setAnswer('に')}
          disabled={disabled}
        >
          に
        </Button>
        <Button
          size="small"
          variant="outlined"
          onClick={() => setAnswer('で')}
          disabled={disabled}
        >
          で
        </Button>
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
    })
  ),
};

export default AnswerInput;
