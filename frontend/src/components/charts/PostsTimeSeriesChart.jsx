import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Paper, Typography } from '@mui/material';
import PropTypes from 'prop-types';
// import { parseISO, format } from 'date-fns'; // If complex date formatting needed for XAxis ticks

const PostsTimeSeriesChart = ({ data, interval = "day" }) => {
  if (!data || data.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 2, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography>No time series data available to display chart.</Typography>
      </Paper>
    );
  }
  // Backend provides: [{"date": "2023-10-26", "count": 15}, ...]
  // Recharts LineChart: XAxis dataKey="date", Line dataKey="count"

  // Optional: Format X-axis ticks if dates are too long or need specific formatting
  // const formatXAxisTick = (tickItem) => {
  //   try {
  //     return format(parseISO(tickItem), 'MMM d'); // Example: "Oct 26"
  //   } catch (e) {
  //     return tickItem; // Fallback for "YYYY-Www" or other non-standard ISO
  //   }
  // };

  return (
    <Paper elevation={3} sx={{ p: 2, height: 300 }}>
      <Typography variant="h6" gutterBottom align="center">Posts Over Time ({interval.charAt(0).toUpperCase() + interval.slice(1)}ly)</Typography>
      <ResponsiveContainer width="100%" height="85%">
        <LineChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            // tickFormatter={formatXAxisTick} // Apply if custom formatting is needed
            // For weekly data like "2023-W42", Recharts might treat it as categorical.
            // If dates are full ISO strings, Recharts can parse them better.
            // For "YYYY-MM-DD" or "YYYY-MM", it usually works well.
            interval="preserveStartEnd" // Adjust interval for tick display if needed
            // angle={-30} textAnchor="end" // Rotate labels if they overlap
          />
          <YAxis allowDecimals={false} />
          <Tooltip
            // labelFormatter={(label) => format(parseISO(label), 'PPP')} // Example for tooltip label
          />
          <Legend />
          <Line type="monotone" dataKey="count" stroke="#8884d8" activeDot={{ r: 8 }} name="Posts"/>
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
};

PostsTimeSeriesChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      date: PropTypes.string.isRequired, // Or PropTypes.any if date format varies significantly
      count: PropTypes.number.isRequired,
    })
  ),
  interval: PropTypes.string,
};

export default PostsTimeSeriesChart;
