import React, { useState, useEffect } from 'react';

// Define our preset moods
const MOOD_MAP = {
  angry: { id: 1, color: '#FF4D4D', label: 'Angry' },
  happy: { id: 2, color: '#FFD700', label: 'Happy' },
  sad: { id: 3, color: '#4169E1', label: 'Sad' },
  indifferent: { id: 4, color: '#A9A9A9', label: 'Indifferent' }
};

// Single mood button component
const MoodButton = ({ mood, isSelected, onClick }) => {
  const { color, label } = MOOD_MAP[mood];
  
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
      {label}
    </button>
  );
};

// Panel component for mood selection
const MoodPanel = ({ title, selectedMood, onMoodSelect }) => {
  return (
    <div className="p-8 bg-white rounded-lg shadow-sm">
      <h2 className="text-2xl mb-8">{title}</h2>
      <div className="flex flex-col gap-2 max-w-md">
        {Object.keys(MOOD_MAP).map((mood) => (
          <MoodButton
            key={mood}
            mood={mood}
            isSelected={selectedMood === mood}
            onClick={onMoodSelect}
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
  
  // Function to fetch all transitions
  const fetchTransitions = async () => {
    try {
      const response = await fetch('http://localhost:8000/transitions');
      const data = await response.json();
      setAllTransitions(data);
    } catch (error) {
      console.error('Error fetching transitions:', error);
    }
  };
  
  // Load transitions when component mounts
  useEffect(() => {
    fetchTransitions();
  }, []);
  
  // Function to save transition to the backend
  const saveTransition = async () => {
    if (!initialMood || !targetMood) {
      setMessage({ text: 'Please select both moods', type: 'error' });
      return;
    }
    
    setIsLoading(true);
    setMessage(null);
    
    try {
      const response = await fetch('http://localhost:8000/transitions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          initial_mood_id: MOOD_MAP[initialMood].id,
          target_mood_id: MOOD_MAP[targetMood].id,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage({ text: 'Transition saved successfully!', type: 'success' });
      
      // Refresh transitions list
      fetchTransitions();
      
      // Optional: reset selections
      // setInitialMood(null);
      // setTargetMood(null);
    } catch (error) {
      console.error('Error saving transition:', error);
      setMessage({ text: `Error: ${error.message}`, type: 'error' });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Mood Transition Tracker</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          <MoodPanel
            title="How are you feeling now?"
            selectedMood={initialMood}
            onMoodSelect={setInitialMood}
          />
          
          <MoodPanel
            title="How would you like to feel?"
            selectedMood={targetMood}
            onMoodSelect={setTargetMood}
          />
        </div>

        {/* Show transition summary when both moods are selected */}
        {initialMood && targetMood && (
          <div className="mt-8 p-6 bg-white rounded-lg shadow-sm text-center">
            <p className="text-lg">
              Transitioning from{' '}
              <span style={{ color: MOOD_MAP[initialMood].color }}>
                {MOOD_MAP[initialMood].label}
              </span>
              {' '}to{' '}
              <span style={{ color: MOOD_MAP[targetMood].color }}>
                {MOOD_MAP[targetMood].label}
              </span>
            </p>
            
            <button 
              onClick={saveTransition}
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