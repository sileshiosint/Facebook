import React from 'react';
import PropTypes from 'prop-types';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  CircularProgress, Typography, Box, TableSortLabel
} from '@mui/material';
import { format } from 'date-fns'; // For date formatting
import RiskBadge from './RiskBadge';
import SentimentBadge from './SentimentBadge';

// Helper to truncate text
const truncateText = (text, maxLength = 100) => {
  if (!text) return 'N/A';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

function PostTable({
  posts,
  isLoading,
  // For sorting - to be implemented fully later
  // sortConfig,
  // requestSort
}) {

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!posts || posts.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="subtitle1">No posts found matching your criteria.</Typography>
      </Paper>
    );
  }

  // Define table headers
  // Add 'id' for sortConfig key if implementing sorting
  const headCells = [
    { id: 'post_text', label: 'Post Text', minWidth: 250 },
    { id: 'user_name', label: 'User', minWidth: 100 },
    { id: 'source_name', label: 'Source', minWidth: 120 }, // Group or Page name
    { id: 'language', label: 'Lang', minWidth: 50, align: 'center' },
    { id: 'sentiment', label: 'Sentiment', minWidth: 100, align: 'center' },
    { id: 'risk_score', label: 'Risk Score', minWidth: 100, align: 'center' },
    { id: 'post_time', label: 'Post Time', minWidth: 150 },
    // Add more columns as needed: e.g., keywords, entities
  ];

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 600 }}> {/* Added maxHeight for scroll */}
      <Table stickyHeader aria-label="sticky posts table">
        <TableHead>
          <TableRow>
            {headCells.map((headCell) => (
              <TableCell
                key={headCell.id}
                align={headCell.align || 'left'}
                style={{ minWidth: headCell.minWidth, fontWeight: 'bold' }}
                // Add sorting props here if sortConfig and requestSort are implemented
                // sortDirection={sortConfig && sortConfig.key === headCell.id ? sortConfig.direction : false}
              >
                {/* <TableSortLabel
                  active={sortConfig && sortConfig.key === headCell.id}
                  direction={sortConfig && sortConfig.key === headCell.id ? sortConfig.direction : 'asc'}
                  onClick={() => requestSort && requestSort(headCell.id)}
                > */}
                  {headCell.label}
                {/* </TableSortLabel> */}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {posts.map((post) => (
            <TableRow hover role="checkbox" tabIndex={-1} key={post.id /* Assuming post objects have a unique 'id' from backend */}>
              <TableCell>
                <Typography variant="body2" title={post.post_text}>
                    {truncateText(post.post_text, 150)}
                </Typography>
                {post.post_url && (
                    <a href={post.post_url} target="_blank" rel="noopener noreferrer" style={{fontSize: '0.8rem'}}>
                        View Post
                    </a>
                )}
              </TableCell>
              <TableCell>{post.user_name || 'N/A'}</TableCell>
              <TableCell>
                {post.source_type === 'page' && post.page_url ? (
                  <a href={post.page_url} target="_blank" rel="noopener noreferrer">{post.page_name || 'View Page'}</a>
                ) : post.source_type === 'group' && post.group_url ? (
                  <a href={post.group_url} target="_blank" rel="noopener noreferrer">{post.group_name || 'View Group'}</a>
                ) : (
                  post.page_name || post.group_name || 'N/A'
                )}
              </TableCell>
              <TableCell align="center">{post.language || 'N/A'}</TableCell>
              <TableCell align="center">
                <SentimentBadge compoundScore={post.sentiment?.compound} />
              </TableCell>
              <TableCell align="center">
                <RiskBadge score={post.risk_score} />
              </TableCell>
              <TableCell>
                {post.post_time ? format(new Date(post.post_time), 'PPpp') : 'N/A'}
                {/* PPpp format: Oct 26, 2023, 10:30:00 AM */}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

PostTable.propTypes = {
  posts: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    post_text: PropTypes.string,
    user_name: PropTypes.string,
    source_type: PropTypes.string,
    page_name: PropTypes.string,
    group_name: PropTypes.string,
    language: PropTypes.string,
    sentiment: PropTypes.object, // Specifically, shape({ compound: PropTypes.number })
    risk_score: PropTypes.number,
    post_time: PropTypes.string, // Assuming ISO string from backend
    post_url: PropTypes.string,
  })),
  isLoading: PropTypes.bool,
  // sortConfig: PropTypes.object,
  // requestSort: PropTypes.func,
};

export default PostTable;
