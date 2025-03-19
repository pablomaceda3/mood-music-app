import React, { useState, useEffect } from 'react';
import SpotifyIntegration from './SpotifyIntegration';
import { fetchMoods, saveTransition, fetchTransitions } from '../services/MoodService';

// Single mood button component
const MoodButton = ({ mood, isSelected, onClick }) => {
  return (
    <button
      onClick={() => onClick(mood)}
      className={`
        w-full p-4 m-2 rounded-lg transition-all
        ${isSelected ? 'ring-2 ring-offset-2 ring-gray-400 scale-105' : 'hover:scale-102'}
      `}
      style={{
        backgroundColor: mood.color,
        color: 'white'
      }}
    >
      {mood.name}
    </button>
  );
};

// Panel component for mood selection
const MoodPanel = ({ title, selectedMood, moods, onMoodSelect }) => {
  return (
    <div className="p-8 bg-white rounded-lg shadow-sm">
      <h2 className="text-2xl mb-8">{title}</h2>
      <div className="flex flex-col gap-2 max-w-md">
        {moods.map((mood) => (
          <MoodButton
            key={mood.id}
            mood={mood}
            isSelected={selectedMood && selectedMood.id === mood.id}
            onClick={() => onMoodSelect(mood)}
          />
        ))}
      </div>
    </div>
  );
};

const MoodTransition = () => {
  const [initialMood, setInitialMood] = useState(null);
  const [targetMood, setTargetMood] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [allTransitions, setAllTransitions] = useState([]);
  const [lastTransition, setLastTransition] = useState(null);
  const [moods, setMoods] = useState([]);
  const [isLoadingMoods, setIsLoadingMoods] = useState(true);
  const [error, setError] = useState(null);
  
  // Function to fetch all moods from the API
  const loadMoods = async () => {
    setIsLoadingMoods(true);
    setError(null);
    
    try {
      const moodsData = await fetchMoods();
      setMoods(moodsData);
    } catch (error) {
      console.error('Error fetching moods:', error);
      setError('Failed to load moods. Please refresh the page.');
    } finally {
      setIsLoadingMoods(false);
    }
  };
  
  // Function to fetch all transitions
  const loadTransitions = async () => {
    try {
      const transitionsData = await fetchTransitions();
      setAllTransitions(transitionsData);
    } catch (error) {
      console.error('Error fetching transitions:', error);
    }
  };
  
  // Load moods and transitions when component mounts
  useEffect(() => {
    loadMoods();
    loadTransitions();
  }, []);
  
  // Function to save transition to the backend
  const handleSaveTransition = async () => {
    if (!initialMood || !targetMood) {
      setMessage({ text: 'Please select both moods', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage(null);
    
    try {
      const data = await saveTransition(initialMood.id, targetMood.id);
      setMessage({ text: 'Transition saved successfully!', type: 'success' });
      
      // Set the last transition for Spotify integration
      setLastTransition(data);
      
      // Refresh transitions list
      loadTransitions();
    } catch (error) {
      console.error('Error saving transition:', error);
      setMessage({ text: `Error: ${error.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle when a playlist is created
  const handlePlaylistCreated = (playlistData) => {
    setMessage({ 
      text: `Playlist created successfully! ${playlistData.track_count} tracks added.`, 
      type: 'success' 
    });
  };
  
  // Show loading state while fetching moods
  if (isLoadingMoods) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl mb-4">Loading moods...</div>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      </div>
    );
  }
  
  // Show error state if mood loading failed
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center text-red-600">
          <div className="text-xl mb-4">{error}</div>
          <button 
            onClick={loadMoods}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Mood Transition Tracker</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <MoodPanel
            title="How are you feeling now?"
            selectedMood={initialMood}
            moods={moods}
            onMoodSelect={setInitialMood}
          />
          
          <MoodPanel
            title="How would you like to feel?"
            selectedMood={targetMood}
            moods={moods}
            onMoodSelect={setTargetMood}
          />
        </div>

        {/* Show transition summary when both moods are selected */}
        {initialMood && targetMood && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-sm text-center">
            <p className="text-lg">
              Transitioning from{' '}
              <span style={{ color: initialMood.color }}>
                {initialMood.name}
              </span>
              {' '}to{' '}
              <span style={{ color: targetMood.color }}>
                {targetMood.name}
              </span>
            </p>
            
            <button 
              onClick={handleSaveTransition}
              disabled={isLoading}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
            >
              {isLoading ? 'Saving...' : 'Save Transition'}
            </button>
            
            {message && (
              <div className={`mt-4 p-2 rounded ${message.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                {message.text}
              </div>
            )}
          </div>
        )}
        
        {/* Spotify Integration */}
        {lastTransition && (
          <SpotifyIntegration 
            moodTransition={lastTransition}
            onPlaylistCreated={handlePlaylistCreated}
          />
        )}
        
        {/* Show recent transitions */}
        {allTransitions.length > 0 && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-sm">
            <h2 className="text-2xl mb-4">Recent Transitions</h2>
            <ul className="divide-y">
              {allTransitions.map(transition => (
                <li key={transition.id} className="py-2">
                  <span style={{ color: transition.initial_mood.color }}>
                    {transition.initial_mood.name}
                  </span>
                  {' → '}
                  <span style={{ color: transition.target_mood.color }}>
                    {transition.target_mood.name}
                  </span>
                  <span className="text-gray-500 text-sm ml-2">
                    {new Date(transition.timestamp).toLocaleString()}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoodTransition;