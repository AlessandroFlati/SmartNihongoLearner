/**
 * Furigana Text Component
 *
 * Displays Japanese text with reading (furigana) above it.
 * Simple implementation showing reading in parentheses.
 */

import { Box, Typography } from '@mui/material';
import PropTypes from 'prop-types';

function FuriganaText({ japanese, reading, english, showReading = true, showEnglish = false, size = 'large' }) {
  const fontSize = {
    small: '1.2rem',
    medium: '1.8rem',
    large: '2.5rem',
    xlarge: '3.5rem',
  }[size] || '2.5rem';

  const readingFontSize = {
    small: '0.7rem',
    medium: '0.9rem',
    large: '1.1rem',
    xlarge: '1.3rem',
  }[size] || '1.1rem';

  return (
    <Box sx={{ textAlign: 'center', my: 2 }}>
      <Typography
        variant="h2"
        component="div"
        sx={{
          fontSize,
          fontWeight: 500,
          fontFamily: 'Noto Sans JP, sans-serif',
          mb: 0.5,
        }}
      >
        {japanese}
      </Typography>

      {showReading && reading && (
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{
            fontSize: readingFontSize,
            fontStyle: 'italic',
            mb: showEnglish ? 1 : 0,
          }}
        >
          {reading}
        </Typography>
      )}

      {showEnglish && english && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            fontSize: '0.9rem',
            mt: 1,
          }}
        >
          {english}
        </Typography>
      )}
    </Box>
  );
}

FuriganaText.propTypes = {
  japanese: PropTypes.string.isRequired,
  reading: PropTypes.string,
  english: PropTypes.string,
  showReading: PropTypes.bool,
  showEnglish: PropTypes.bool,
  size: PropTypes.oneOf(['small', 'medium', 'large', 'xlarge']),
};

export default FuriganaText;
