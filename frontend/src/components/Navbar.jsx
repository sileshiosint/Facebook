import React from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

function Navbar() {
  const { isAuthenticated, user, logoutUser, isLoading } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutUser();
    navigate('/login'); // Redirect to login after logout
  };

  return (
    <AppBar position="static" sx={{ marginBottom: '2rem' }}> {/* Added margin bottom */}
      <Toolbar>
        <Typography variant="h6" component={RouterLink} to="/" sx={{ color: 'inherit', textDecoration: 'none' }}>
          OSINT Dashboard
        </Typography>
        <Box sx={{ flexGrow: 1 }} /> {/* This will push subsequent items to the right */}

        {isLoading ? (
          <Typography variant="body2" sx={{ color: 'inherit', marginRight: 2 }}>Loading Auth...</Typography>
        ) : isAuthenticated && user ? (
          <>
            <Button color="inherit" component={RouterLink} to="/analytics">Analytics</Button>
            <Button color="inherit" component={RouterLink} to="/scraped-profiles">Profiles</Button> {/* Added Profiles Link */}
            <Typography variant="subtitle1" sx={{ color: 'inherit', marginRight: 2, marginLeft: 2 }}>
              Welcome, {user.username}
            </Typography>
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </>
        ) : (
          <Button color="inherit" component={RouterLink} to="/login">
            Login
          </Button>
        )}
        {/* Example link to a registration page - create this page similarly to LoginPage */}
        {/* {!isAuthenticated && !isLoading && (
          <Button color="inherit" component={RouterLink} to="/register" sx={{ ml: 1 }}>
            Register
          </Button>
        )} */}
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
