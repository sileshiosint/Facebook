import React, { useState, useEffect, useCallback } from 'react';
import profileService from '../services/profileService'; // Ensure this path is correct
import ProfileTable from '../components/ProfileTable';   // Ensure this path is correct
import {
  Container, Typography, Box, TextField, Button, Grid, Paper,
  CircularProgress, Alert, TablePagination
} from '@mui/material';

function ScrapedProfilesPage() {
  const [profiles, setProfiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Filters State - basic keyword search for profiles
  const [keyword, setKeyword] = useState('');

  // Pagination State
  const [page, setPage] = useState(0); // MUI TablePagination is 0-indexed
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalProfiles, setTotalProfiles] = useState(0);

  const fetchProfiles = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const params = {
        skip: page * rowsPerPage,
        limit: rowsPerPage,
        keyword: keyword || undefined,
      };
      const response = await profileService.getProfiles(params); // Expects { data: [], total_count: X }
      setProfiles(response.data);
      setTotalProfiles(response.total_count);
    } catch (err) {
      console.error("Failed to fetch profiles:", err);
      setError(err.response?.data?.detail || 'Failed to fetch profiles.');
      setProfiles([]);
    } finally {
      setIsLoading(false);
    }
  }, [page, rowsPerPage, keyword]);

  useEffect(() => {
    fetchProfiles();
  }, [fetchProfiles]);

  const handleFilterChange = () => {
    setPage(0);
    fetchProfiles();
  };

  const handleKeywordChange = (event) => {
    setKeyword(event.target.value);
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom sx={{ mt: 2, mb: 3 }}>
        Scraped Profiles
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Filters</Typography>
        <Grid container spacing={2} alignItems="flex-end">
          <Grid item xs={12} sm={9}>
            <TextField
              fullWidth
              label="Search by User Name"
              variant="outlined"
              value={keyword}
              onChange={handleKeywordChange}
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <Button
              variant="contained"
              onClick={handleFilterChange}
              disabled={isLoading}
              fullWidth
            >
              Search Profiles
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <ProfileTable profiles={profiles} isLoading={isLoading} />

      <TablePagination
        component="div"
        count={totalProfiles}
        page={page}
        onPageChange={handlePageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleRowsPerPageChange}
        rowsPerPageOptions={[5, 10, 25, 50]}
      />
    </Container>
  );
}

export default ScrapedProfilesPage;
