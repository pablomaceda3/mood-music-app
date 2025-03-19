// API service for mood transitions
const API_URL = 'http://localhost:8000/api/v1';

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

// Fetch a specific mood by ID
export const fetchMood = async (moodId) => {
  try {
    const response = await fetch(`${API_URL}/moods/${moodId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching mood with ID ${moodId}:`, error);
    throw error;
  }
};

// Create a new mood (admin functionality)
export const createMood = async (moodData) => {
  try {
    const response = await fetch(`${API_URL}/moods`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(moodData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating mood:', error);
    throw error;
  }
};

// Update an existing mood (admin functionality)
export const updateMood = async (moodId, moodData) => {
  try {
    const response = await fetch(`${API_URL}/moods/${moodId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(moodData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error updating mood with ID ${moodId}:`, error);
    throw error;
  }
};

// Delete a mood (admin functionality)
export const deleteMood = async (moodId) => {
  try {
    const response = await fetch(`${API_URL}/moods/${moodId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return true; // Successful deletion
  } catch (error) {
    console.error(`Error deleting mood with ID ${moodId}:`, error);
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

// Fetch a specific transition by ID
export const fetchTransition = async (transitionId) => {
  try {
    const response = await fetch(`${API_URL}/transitions/${transitionId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching transition with ID ${transitionId}:`, error);
    throw error;
  }
};

// Delete a transition
export const deleteTransition = async (transitionId) => {
  try {
    const response = await fetch(`${API_URL}/transitions/${transitionId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return true; // Successful deletion
  } catch (error) {
    console.error(`Error deleting transition with ID ${transitionId}:`, error);
    throw error;
  }
};