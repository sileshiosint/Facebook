import React from 'react';
import PropTypes from 'prop-types';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  CircularProgress, Typography, Box, Link as MuiLink
} from '@mui/material';
import { format } from 'date-fns';

function ProfileTable({ profiles, isLoading }) {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" sx={{ p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!profiles || profiles.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="subtitle1">No profiles found.</Typography>
      </Paper>
    );
  }

  const headCells = [
    { id: 'user_name', label: 'User Name', minWidth: 170 },
    { id: 'profile_url', label: 'Profile URL', minWidth: 200 },
    { id: 'keyword_search_term', label: 'Searched Keyword', minWidth: 150 },
    { id: 'scraped_timestamp', label: 'Scraped Timestamp', minWidth: 170 },
  ];

  return (
    <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
      <Table stickyHeader aria-label="sticky profiles table">
        <TableHead>
          <TableRow>
            {headCells.map((headCell) => (
              <TableCell
                key={headCell.id}
                align={headCell.align || 'left'}
                style={{ minWidth: headCell.minWidth, fontWeight: 'bold' }}
              >
                {headCell.label}
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {profiles.map((profile) => (
            <TableRow hover tabIndex={-1} key={profile.id}>
              <TableCell>{profile.user_name || 'N/A'}</TableCell>
              <TableCell>
                {profile.profile_url ? (
                  <MuiLink href={profile.profile_url} target="_blank" rel="noopener noreferrer">
                    {profile.profile_url}
                  </MuiLink>
                ) : 'N/A'}
              </TableCell>
              <TableCell>{profile.keyword_search_term || 'N/A'}</TableCell>
              <TableCell>
                {profile.scraped_timestamp ? format(new Date(profile.scraped_timestamp), 'PPpp') : 'N/A'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

ProfileTable.propTypes = {
  profiles: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.string.isRequired,
    user_name: PropTypes.string,
    profile_url: PropTypes.string,
    keyword_search_term: PropTypes.string,
    scraped_timestamp: PropTypes.string, // Assuming ISO string
  })),
  isLoading: PropTypes.bool,
};

export default ProfileTable;
