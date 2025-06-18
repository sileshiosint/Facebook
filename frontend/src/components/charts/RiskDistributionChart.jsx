import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'; // Added Cell
import { Paper, Typography }_from '@mui/material';
import PropTypes from 'prop-types';

const RiskDistributionChart = ({ data }) => {
  if (!data || data.length === 0 || data.every(item => item.count === 0)) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography>No risk data available to display chart.</Typography>
      </Paper>
    );
  }

  const getColor = (category) => {
    if (category === 'Low') return '#4caf50'; // Green
    if (category === 'Medium') return '#ff9800'; // Orange
    if (category === 'High') return '#f44336'; // Red
    return '#8884d8'; // Default for "Unknown" or "Other" if they appear
  };

  // Ensure data has the 'category' field for XAxis dataKey
  // The backend provides: [{"category": "Low", "count": 0}, ...] which is good.

  return (
    <Paper elevation={3} sx={{ p: 2, height: 300 }}>
      <Typography variant="h6" gutterBottom align="center">Risk Category Distribution</Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="category" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Legend />
          <Bar dataKey="count">
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.category)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
};

RiskDistributionChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      category: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
    })
  ),
};

export default RiskDistributionChart;
