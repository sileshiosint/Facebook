import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom'; // For potential registration link
import { useAuth } from '../contexts/AuthContext';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress'; // For loading indicator

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { loginUser, isLoading: authIsLoading } = useAuth(); // Renamed isLoading to avoid conflict
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false); // Local submitting state

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await loginUser(username, password);
      navigate('/');
    } catch (err) {
      console.error("Login page error:", err);
      setError(err.response?.data?.detail || 'Failed to login. Please check your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Combine auth context loading with local submitting state
  const isLoading = authIsLoading || isSubmitting;

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
        {error && <Alert severity="error" sx={{ width: '100%', mt: 2, mb: 1 }}>{error}</Alert>}
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="username"
            label="Username"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isLoading}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
          />
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Sign In'}
          </Button>
          {/* Example link to register page, if you add one */}
          {/* <Box textAlign="center">
            <RouterLink to="/register" variant="body2">
              {"Don't have an account? Sign Up"}
            </RouterLink>
          </Box> */}
        </Box>
      </Box>
    </Container>
  );
}

export default LoginPage;
