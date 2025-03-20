import React, { useState, useEffect } from 'react';
import SpotifyIntegration from './SpotifyIntegration';
import { fetchMoods, saveTransition, fetchTransitions } from '../services/MoodService';
import { getCurrentUser } from '../services/AuthService';

// Single mood button component
const MoodButton = ({ mood, isSelected, onClick }) => {
  const { color, name } = mood;
  
  return (
    <button
      onClick={() => onClick(mood)}
      className={`
        w-full p-4 m-2 rounded-lg transition-all
        ${isSelected ? 'ring-2 ring-offset-2 ring-gray-400 scale-105' : 'hover:scale-102'}
      `}
      style={{
        backgroundColor: color,
        color: 'white'
      }}
    >
      {name}
    </button>
  );
};

// Panel component for mood selection
const MoodPanel = ({ title, selectedMood, moods, onMoodSelect, isLoading }) => {
  return (
    <div className="p-8 bg-white rounded-lg shadow-sm">
      <h2 className="text-2xl mb-8">{title}</h2>
      <div className="flex flex-col gap-2 max-w-md">
        {isLoading ? (
          <div className="text-center py-4">Loading moods...</div>
        ) : moods.length > 0 ? (
          moods.map((mood) => (
            <MoodButton
              key={mood.id}
              mood={mood}
              isSelected={selectedMood && selectedMood.id === mood.id}
              onClick={onMoodSelect}
            />
          ))
        ) : (
          <div className="text-center py-4">No moods available</div>
        )}
      </div>
    </div>
  );
};

const MoodTransition = ({ showHistory = false }) => {
  const [initialMood, setInitialMood] = useState(null);
  const [targetMood, setTargetMood] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMoodsLoading, setIsMoodsLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [allTransitions, setAllTransitions] = useState([]);
  const [lastTransition, setLastTransition] = useState(null);
  const [moods, setMoods] = useState([]);
  const [user, setUser] = useState(null);
  
  // Function to fetch all transitions
  const loadTransitions = async () => {
    try {
      setIsLoading(true);
      const data = await fetchTransitions();
      setAllTransitions(data);
      
      // Set the last transition for Spotify integration
      if (data.length > 0) {
        setLastTransition(data[0]);
      }
    } catch (error) {
      console.error('Error fetching transitions:', error);
      setMessage({ text: `Error loading transitions: ${error.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Function to fetch moods
  const loadMoods = async () => {
    try {
      setIsMoodsLoading(true);
      const moodsData = await fetchMoods();
      setMoods(moodsData);
    } catch (error) {
      console.error('Error fetching moods:', error);
      setMessage({ text: `Error loading moods: ${error.message}`, type: 'error' });
    } finally {
      setIsMoodsLoading(false);
    }
  };
  
  // Load user data, moods, and transitions when component mounts
  useEffect(() => {
    const initData = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        
        await loadMoods();
        await loadTransitions();
      } catch (error) {
        console.error('Error initializing data:', error);
      }
    };
    
    initData();
  }, [showHistory]);
  
  // Function to save transition to the backend
  const handleSaveTransition = async () => {
    if (!initialMood || !targetMood) {
      setMessage({ text: 'Please select both moods', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage(null);
    
    try {
      const response = await saveTransition(initialMood.id, targetMood.id);
      setMessage({ text: 'Transition saved successfully!', type: 'success' });
      
      // Set the last transition for Spotify integration
      setLastTransition(response);
      
      // Refresh transitions list
      await loadTransitions();
      
      // Optional: reset selections after saving
      // setInitialMood(null);
      // setTargetMood(null);
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
  
  // If showing the history view
  if (showHistory) {
    return (
      <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">My Mood Transitions</h1>
        
        {isLoading ? (
          <div className="text-center py-8">Loading your transitions...</div>
        ) : allTransitions.length > 0 ? (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {allTransitions.map(transition => (
                <li key={transition.id}>
                  <div className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
                    <div className="flex items-center">
                      <div className="min-w-0 flex-1">
                        <p className="text-lg font-medium text-gray-900 truncate">
                          <span style={{ color: transition.initial_mood.color }}>
                            {transition.initial_mood.name}
                          </span>
                          {' → '}
                          <span style={{ color: transition.target_mood.color }}>
                            {transition.target_mood.name}
                          </span>
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(transition.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="text-center py-8 bg-white rounded-lg shadow">
            <p className="text-gray-500">You haven't recorded any mood transitions yet.</p>
          </div>
        )}
      </div>
    );
  }
  
  // Default view (mood transition tracker)
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Mood Transition Tracker</h1>
        
        {user && (
          <div className="text-center mb-4">
            <p className="text-gray-600">Welcome, {user.username}!</p>
          </div>
        )}
        
        <div className="grid md:grid-cols-2 gap-8">
          <MoodPanel
            title="How are you feeling now?"
            selectedMood={initialMood}
            moods={moods}
            onMoodSelect={setInitialMood}
            isLoading={isMoodsLoading}
          />
          
          <MoodPanel
            title="How would you like to feel?"
            selectedMood={targetMood}
            moods={moods}
            onMoodSelect={setTargetMood}
            isLoading={isMoodsLoading}
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
              {allTransitions.slice(0, 5).map(transition => (
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