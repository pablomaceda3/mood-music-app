// API service for mood transitions
const API_URL = 'http://localhost:8000';

// Fetch all available moods
export const fetchMoods = async () => {
  try {
    const response = await fetch(`${API_URL}/moods`);
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
      headers: {
        'Content-Type': 'application/json',
      },
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

// Fetch all transitions
export const fetchTransitions = async () => {
  try {
    const response = await fetch(`${API_URL}/transitions`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching transitions:', error);
    throw error;
  }
};