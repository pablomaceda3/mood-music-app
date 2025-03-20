// API service for authentication
const API_URL = 'http://localhost:8000/api/v1';

// Register a new user
export const registerUser = async (username, email, password) => {
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username,
        email,
        password,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Registration failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error registering user:', error);
    throw error;
  }
};

// Login and get token
export const loginUser = async (username, password) => {
  try {
    // For OAuth2 password flow, we need to use form data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }
    
    const data = await response.json();
    
    // Store the token in localStorage
    localStorage.setItem('token', data.access_token);
    
    return data;
  } catch (error) {
    console.error('Error logging in:', error);
    throw error;
  }
};

// Get the current user's profile
export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }
    
    const response = await fetch(`${API_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        // Token invalid or expired, clear it
        localStorage.removeItem('token');
      }
      throw new Error('Failed to get user profile');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

// Logout the user
export const logoutUser = () => {
  localStorage.removeItem('token');
};

// Check if user is logged in
export const isAuthenticated = () => {
  return localStorage.getItem('token') !== null;
};

// Get authentication token
export const getAuthToken = () => {
  return localStorage.getItem('token');
};