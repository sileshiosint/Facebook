import React from 'react';
import Chip from '@mui/material/Chip';
import PropTypes from 'prop-types';

function SentimentBadge({ compoundScore }) {
  let color = 'default';
  let label = 'Neutral';

  if (compoundScore === null || compoundScore === undefined) {
    label = 'N/A';
  } else if (compoundScore > 0.05) {
    color = 'success';
    label = 'Positive';
  } else if (compoundScore < -0.05) {
    color = 'error';
    label = 'Negative';
  }
  // else it remains 'default' and 'Neutral'

  // You can also display the score if desired:
  // label = `${label} (${compoundScore !== null && compoundScore !== undefined ? compoundScore.toFixed(2) : ''})`;


  return <Chip label={label} color={color} size="small" variant="outlined"/>;
}

SentimentBadge.propTypes = {
  // The compound score from VADER is a float between -1 and 1
  compoundScore: PropTypes.number,
};

export default SentimentBadge;
