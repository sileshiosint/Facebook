import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL, // Ensure this var is set in .env files
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Optional: Add response interceptor for global error handling (e.g., 401 for logout)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Example: Token expired or invalid, redirect to login
      // This depends on how you want to handle global 401s.
      // localStorage.removeItem('authToken');
      // window.location.href = '/login'; // Force redirect
      console.error("Unauthorized or token expired, handle logout globally if needed.");
    }
    return Promise.reject(error);
  }
);


export default apiClient;
