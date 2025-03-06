import React, { useState } from 'react';

// Define our preset moods
const PRESET_MOODS = {
  angry: { color: '#FF4D4D', label: 'Angry' },
  happy: { color: '#FFD700', label: 'Happy' },
  sad: { color: '#4169E1', label: 'Sad' },
  indifferent: { color: '#A9A9A9', label: 'Indifferent' }
};

// Single mood button component
const MoodButton = ({ mood, isSelected, onClick }) => {
  const { color, label } = PRESET_MOODS[mood];
  
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
        {Object.keys(PRESET_MOODS).map((mood) => (
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
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
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
              <span style={{ color: PRESET_MOODS[initialMood].color }}>
                {PRESET_MOODS[initialMood].label}
              </span>
              {' '}to{' '}
              <span style={{ color: PRESET_MOODS[targetMood].color }}>
                {PRESET_MOODS[targetMood].label}
              </span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MoodTransition;