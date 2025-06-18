import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography } from '@mui/material';
import PropTypes from 'prop-types';

// Basic colors for pie chart slices, can be expanded
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#FF4560', '#00E396'];

const LanguageDistributionChart = ({ data }) => {
  if (!data || data.length === 0 || data.every(item => item.count === 0)) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography>No language data available to display chart.</Typography>
      </Paper>
    );
  }
  // Recharts Pie expects `name` (for label) and `value` (for size) keys
  // Backend provides: [{"language": "en", "count": 500}, ...]
  // So we map `language` to `name` and `count` to `value`.
  const chartData = data.map(item => ({ name: item.language, value: item.count }));

  return (
    <Paper elevation={3} sx={{ p: 2, height: 300 }}>
      <Typography variant="h6" gutterBottom align="center">Language Distribution</Typography>
      <ResponsiveContainer width="100%" height="85%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            // label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`} // Example label
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Paper>
  );
};

LanguageDistributionChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      language: PropTypes.string.isRequired,
      count: PropTypes.number.isRequired,
    })
  ),
};

export default LanguageDistributionChart;
