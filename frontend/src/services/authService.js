import apiClient from './api';

const login = async (username, password) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  // If your FastAPI /token endpoint strictly follows OAuth2 and expects grant_type:
  // params.append('grant_type', 'password');
  // params.append('scope', ''); // Adjust scope as needed by your backend

  const response = await apiClient.post('/token', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  if (response.data.access_token) {
    localStorage.setItem('authToken', response.data.access_token);
    // The backend /token endpoint currently returns: {"access_token": "...", "token_type": "bearer"}
    // It does not return user details directly. User details are fetched via /users/me/
  }
  return response.data; // Returns {access_token, token_type}
};

const register = async (username, password, email) => {
    const response = await apiClient.post('/users/register/', {
        username,
        password,
        email // Optional based on your schema and backend validation
    });
    return response.data; // Returns the created user (without password)
};

const logout = () => {
  localStorage.removeItem('authToken');
  // Also consider clearing any other user-related state from context or other storage
  // For example, if user details were stored separately in localStorage:
  // localStorage.removeItem('currentUser');
  console.log("Logged out, token removed.");
};

const getCurrentUser = async () => {
    const token = localStorage.getItem('authToken');
    if (!token) {
        // console.log("No token found, cannot fetch current user.");
        return null;
    }
    try {
        // apiClient already includes the token in its request interceptor
        const response = await apiClient.get('/users/me/');
        // console.log("Fetched current user:", response.data);
        return response.data; // Returns user details from schemas.User (id, username, email, disabled)
    } catch (error) {
        console.error("Failed to fetch current user:", error.response?.data || error.message);
        // If error is 401 (e.g. token invalid/expired), the global response interceptor in api.js
        // might already handle logout. Or handle it more explicitly here if needed.
        if (error.response && error.response.status === 401) {
            logout(); // Ensure token is cleared if server rejects it
        }
        return null;
    }
};

export default { login, logout, getCurrentUser, register };
