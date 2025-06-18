import React, { createContext, useState, useContext, useEffect } from 'react';
import apiClient from '../services/api'; // Import apiClient to update its defaults if needed
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('authToken'));
  // Initialize isAuthenticated based on the presence of a token.
  // useEffect will then validate this token and update state.
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('authToken'));
  const [isLoading, setIsLoading] = useState(true); // Start with loading true

  useEffect(() => {
    const initializeAuth = async () => {
      const currentToken = localStorage.getItem('authToken');
      if (currentToken) {
        // We have a token, let's try to validate it by fetching the user
        // The apiClient interceptor will automatically use this token.
        try {
          const currentUser = await authService.getCurrentUser();
          if (currentUser) {
            setUser(currentUser);
            setIsAuthenticated(true);
            setToken(currentToken); // Ensure token state is also set
          } else {
            // Token might be invalid or user not found
            authService.logout(); // Clear invalid token
            setUser(null);
            setIsAuthenticated(false);
            setToken(null);
          }
        } catch (error) {
          console.error("Initialization: Failed to fetch user with stored token.", error);
          authService.logout(); // Clear invalid token
          setUser(null);
          setIsAuthenticated(false);
          setToken(null);
        }
      }
      setIsLoading(false);
    };
    initializeAuth();
  }, []); // Run only once on component mount

  const loginUser = async (username, password) => {
    setIsLoading(true);
    try {
      const loginData = await authService.login(username, password); // Stores token in localStorage
      setToken(loginData.access_token);
      // After token is set, fetch user details
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
      setIsAuthenticated(true);
      setIsLoading(false);
      return currentUser;
    } catch (error) {
      console.error("AuthContext: Login failed", error);
      authService.logout(); // Clear any partial auth state
      setUser(null);
      setToken(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      throw error; // Re-throw for the login page to handle
    }
  };

  const registerUser = async (username, password, email) => {
    // No setIsLoading here, as registration doesn't immediately log in the user by default
    try {
      const data = await authService.register(username, password, email);
      // Depending on app flow, you might log in the user here automatically
      // or redirect them to the login page.
      return data; // Returns registered user data
    } catch (error) {
      console.error("AuthContext: Registration failed", error);
      throw error; // Re-throw for the registration page to handle
    }
  };

  const logoutUser = () => {
    authService.logout();
    setUser(null);
    setToken(null);
    setIsAuthenticated(false);
    // Optionally redirect to login page or home page via useNavigate if called from a component
    // For now, just updates context state. Navigation can be handled in component calling logout.
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated, isLoading, loginUser, logoutUser, registerUser, setUser, setIsAuthenticated, setToken }}>
      {/* Pass setToken for cases where token might be refreshed by a different mechanism if needed */}
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined && process.env.NODE_ENV === 'development') {
    // This check is more relevant if AuthContext could be null (which it isn't here due to default value)
    // console.warn('useAuth must be used within an AuthProvider');
  }
  if (context === null && process.env.NODE_ENV === 'development') {
     console.warn('AuthContext is null, ensure AuthProvider is wrapping your component tree.');
  }
  return context;
};
