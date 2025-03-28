import axios from 'axios';

// Base URL will be configured for development/production environments
const API_BASE_URL = 'https://api.socialskillscoach.com/v1'; // Placeholder URL

// Create an axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API service functions
const apiService = {
  // Auth endpoints
  auth: {
    login: (email, password) => 
      api.post('/auth/login', { email, password }),
    
    register: (userData) => 
      api.post('/auth/register', userData),
    
    logout: () => 
      api.post('/auth/logout'),
    
    refreshToken: () => 
      api.post('/auth/refresh'),
  },
  
  // User endpoints
  user: {
    getProfile: () => 
      api.get('/user/profile'),
    
    updateProfile: (userData) => 
      api.put('/user/profile', userData),
    
    updateSettings: (settings) => 
      api.put('/user/settings', settings),
    
    getProgress: () => 
      api.get('/user/progress'),
  },
  
  // Practice endpoints
  practice: {
    startSession: (sessionType) => 
      api.post('/practice/session', { sessionType }),
    
    sendMessage: (sessionId, message) => 
      api.post(`/practice/session/${sessionId}/message`, { message }),
    
    getFeedback: (sessionId, messageId) => 
      api.get(`/practice/session/${sessionId}/feedback/${messageId}`),
    
    endSession: (sessionId) => 
      api.post(`/practice/session/${sessionId}/end`),
    
    getHistory: (limit = 10, offset = 0) => 
      api.get(`/practice/history?limit=${limit}&offset=${offset}`),
  },
};

export default apiService; 