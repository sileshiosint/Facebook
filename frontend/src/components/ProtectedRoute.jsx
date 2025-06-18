import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import CircularProgress from '@mui/material/CircularProgress'; // MUI loading spinner
import Box from '@mui/material/Box';

const ProtectedRoute = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    // Display a centered loading spinner
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="80vh" // Take up most of the viewport height
      >
        <CircularProgress />
      </Box>
    );
  }

  // After loading, if still not authenticated, redirect to login.
  // The `replace` prop is important to replace the current entry in history,
  // so the user doesn't get stuck in a redirect loop if they hit the back button.
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
