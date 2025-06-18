import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography } from '@mui/material';
import PropTypes from 'prop-types';

const TopEntitiesChart = ({ data, entityType = "Entities" }) => {
  if (!data || data.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography>No {entityType.toLowerCase()} data available to display chart.</Typography>
      </Paper>
    );
  }
  // Backend provides: [{"entity": "John Doe", "label": "PERSON", "count": 25}, ...]
  // Recharts BarChart: YAxis dataKey="entity", Bar dataKey="count" for horizontal
  // For labels, we can combine entity and label if needed, or just use entity.

  return (
    <Paper elevation={3} sx={{ p: 2, height: 300 }}>
      <Typography variant="h6" gutterBottom align="center">Top {entityType}</Typography>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 50, bottom: 5 }}> {/* Increased left margin for labels */}
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" allowDecimals={false} />
          <YAxis dataKey="entity" type="category" width={100} interval={0} /> {/* Ensure all labels are shown if possible */}
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#82ca9d" nameKey="entity" />
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  );
};

TopEntitiesChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      entity: PropTypes.string.isRequired,
      label: PropTypes.string,
      count: PropTypes.number.isRequired,
    })
  ),
  entityType: PropTypes.string,
};

export default TopEntitiesChart;
