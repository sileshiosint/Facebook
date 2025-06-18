import React from 'react';
import Chip from '@mui/material/Chip';
import PropTypes from 'prop-types';

function RiskBadge({ score }) {
  let color = 'default';
  let label = `Risk: ${score}`;

  if (score === null || score === undefined) {
    label = 'N/A';
    color = 'default';
  } else if (score <= 30) {
    color = 'success'; // Green
    // label = `Low Risk (${score})`;
  } else if (score <= 70) {
    color = 'warning'; // Orange
    // label = `Medium Risk (${score})`;
  } else {
    color = 'error';   // Red
    // label = `High Risk (${score})`;
  }

  return <Chip label={label} color={color} size="small" variant="outlined" />;
}

RiskBadge.propTypes = {
  score: PropTypes.number,
};

export default RiskBadge;
