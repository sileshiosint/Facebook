import React, { useState, useEffect, useCallback } from 'react';
import postService from '../services/postService';
import PostTable from '../components/PostTable';
import {
  Container, Typography, Box, TextField, Button, Grid, Paper,
  Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert,
  TablePagination
} from '@mui/material';
import { debounce } from '@mui/material/utils'; // For debouncing keyword input

function DashboardPage() {
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Filters State
  const [keyword, setKeyword] = useState('');
  const [minRiskScore, setMinRiskScore] = useState(''); // Empty string for 'Any'
  const [language, setLanguage] = useState('');       // Empty string for 'Any'
  const [sourceType, setSourceType] = useState('');   // Empty string for 'Any'

  // Pagination State
  const [page, setPage] = useState(0); // MUI TablePagination is 0-indexed
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalPosts, setTotalPosts] = useState(0); // Assuming backend will provide total count for pagination

  // Sorting state (basic example, can be expanded)
  const [sortBy, setSortBy] = useState('post_time');
  const [sortOrder, setSortOrder] = useState('desc');


  const fetchPosts = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const filters = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        keyword: keyword || undefined, // Send undefined if empty so backend doesn't filter by empty string
        min_risk_score: minRiskScore === '' ? undefined : Number(minRiskScore),
        language: language || undefined,
        source_type: sourceType || undefined,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      // Ideally, the backend should return { items: [], total: ... }
      // For now, assuming it returns just the list of posts and we can't get total for pagination easily
      // Without total count from API, pagination will be limited.
      // Let's assume for now `getPosts` just returns the array.
      const response = await postService.getPosts(filters); // response is now { data: [], total_count: X }
      setPosts(response.data);
      setTotalPosts(response.total_count);

    } catch (err) {
      console.error("Failed to fetch posts:", err);
      setError(err.response?.data?.detail || 'Failed to fetch posts.');
      setPosts([]); // Clear posts on error
    } finally {
      setIsLoading(false);
    }
  }, [page, rowsPerPage, keyword, minRiskScore, language, sourceType, sortBy, sortOrder]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]); // Rerun when fetchPosts (due to its dependencies) changes

  const handleFilterChange = () => {
    setPage(0); // Reset to first page when filters change
    fetchPosts(); // fetchPosts is already memoized by useCallback and will be called by useEffect
  };

  // Debounce keyword input if desired (e.g., to prevent API calls on every keystroke)
  // const debouncedFetchPosts = useCallback(debounce(fetchPosts, 500), [fetchPosts]);
  // For keyword, you might call debouncedFetchPosts in its onChange or a separate useEffect.
  // For simplicity, using a button for now.

  const handleKeywordChange = (event) => {
    setKeyword(event.target.value);
  };
  const handleRiskScoreChange = (event) => {
    setMinRiskScore(event.target.value);
  };
  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
  };
  const handleSourceTypeChange = (event) => {
    setSourceType(event.target.value);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // Reset to first page
  };

  // Placeholder for sorting handler
  // const handleSortRequest = (property) => { ... setSortBy, setSortOrder ... };


  return (
    <Container maxWidth="lg"> {/* lg for wider content area */}
      <Typography variant="h4" gutterBottom sx={{ mt: 2, mb: 3 }}>
        OSINT Dashboard - Posts
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Filters</Typography>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              label="Keyword"
              variant="outlined"
              value={keyword}
              onChange={handleKeywordChange}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>Min Risk Score</InputLabel>
              <Select
                value={minRiskScore}
                onChange={handleRiskScoreChange}
                label="Min Risk Score"
              >
                <MenuItem value=""><em>Any</em></MenuItem>
                <MenuItem value={0}>Low (0+)</MenuItem>
                <MenuItem value={31}>Medium (31+)</MenuItem>
                <MenuItem value={71}>High (71+)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="Language (e.g., en, es)"
              variant="outlined"
              value={language}
              onChange={handleLanguageChange}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth variant="outlined" size="small">
              <InputLabel>Source Type</InputLabel>
              <Select
                value={sourceType}
                onChange={handleSourceTypeChange}
                label="Source Type"
              >
                <MenuItem value=""><em>Any</em></MenuItem>
                <MenuItem value="group">Group</MenuItem>
                <MenuItem value="page">Page</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Button
              variant="contained"
              onClick={handleFilterChange}
              disabled={isLoading}
              fullWidth
            >
              Apply Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <PostTable posts={posts} isLoading={isLoading} />

      {/* Basic pagination based on current items, not ideal without total count from API */}
      <TablePagination
        component="div"
        count={totalPosts} // This needs to come from API for accuracy
        page={page}
        onPageChange={handlePageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleRowsPerPageChange}
        // Options for rows per page
        rowsPerPageOptions={[5, 10, 25, 50]}
        // Note: If totalPosts is not accurately fetched from the API,
        // pagination might behave unexpectedly on the last page.
      />
    </Container>
  );
}

export default DashboardPage;
