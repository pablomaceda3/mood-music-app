// API service for mood transitions
import { getAuthToken } from './AuthService';

const API_URL = 'http://localhost:8000/api/v1';

// Helper function to get auth headers
const getHeaders = () => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Fetch all available moods
export const fetchMoods = async () => {
  try {
    const response = await fetch(`${API_URL}/moods`, {
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching moods:', error);
    throw error;
  }
};

// Save a mood transition
export const saveTransition = async (initialMoodId, targetMoodId) => {
  try {
    const response = await fetch(`${API_URL}/transitions`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        initial_mood_id: initialMoodId,
        target_mood_id: targetMoodId,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error saving transition:', error);
    throw error;
  }
};

// Fetch all transitions for the current user
export const fetchTransitions = async () => {
  try {
    const response = await fetch(`${API_URL}/transitions`, {
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching transitions:', error);
    throw error;
  }
};

// Fetch transitions stats
export const fetchTransitionStats = async () => {
  try {
    const response = await fetch(`${API_URL}/transitions/stats/common`, {
      headers: getHeaders(),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching transition stats:', error);
    throw error;
  }
};