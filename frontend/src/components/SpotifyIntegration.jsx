import React, { useState, useEffect } from 'react';

const SpotifyIntegration = ({ onPlaylistCreated, moodTransition }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isCreatingPlaylist, setIsCreatingPlaylist] = useState(false);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [error, setError] = useState(null);
  
  // Check if user is already authenticated with Spotify
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:8000/spotify/me');
        if (response.ok) {
          setIsAuthenticated(true);
        }
      } catch (err) {
        // Not authenticated yet, which is fine
        console.log('Not authenticated with Spotify yet');
      }
    };
    
    checkAuth();
  }, []);
  
  // Function to authenticate with Spotify
  const authenticateWithSpotify = () => {
    // Redirect to the backend login route
    window.location.href = 'http://localhost:8000/spotify/login';
  };
  
  // Function to create a playlist based on the mood transition
  const createPlaylist = async () => {
    if (!moodTransition) {
      setError('No mood transition available to create a playlist from');
      return;
    }
    
    setIsCreatingPlaylist(true);
    setError(null);
    
      // In the createPlaylist function:
    try {
      const response = await fetch('http://localhost:8000/spotify/create-playlist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          initial_mood_id: moodTransition.initial_mood_id,
          target_mood_id: moodTransition.target_mood_id,
          transition_id: moodTransition.id
        }),
      });
      
      // Add this check to see what's happening with redirects
      if (response.redirected) {
        console.log("Request was redirected to:", response.url);
        window.location.href = response.url;
        return;
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create playlist: ${response.status} - ${errorText}`);
      }
  
      const data = await response.json();
      setPlaylistUrl(data.playlist_url);
      
      if (onPlaylistCreated) {
        onPlaylistCreated(data);
      }
    } catch (err) {
      setError(`Error creating playlist: ${err.message}`);
      console.error(err);
    } finally {
      setIsCreatingPlaylist(false);
    }
  };
  
  return (
    <div className="mt-6 p-4 bg-white rounded-lg shadow">
      <h3 className="text-xl font-semibold mb-3">Spotify Integration</h3>
      
      {!isAuthenticated ? (
        <div>
          <p className="mb-3">Connect with Spotify to create mood transition playlists</p>
          <button
            onClick={authenticateWithSpotify}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
          >
            Connect to Spotify
          </button>
        </div>
      ) : (
        <div>
          {!playlistUrl ? (
            <div>
              <p className="mb-3">Create a playlist based on your mood transition</p>
              <button
                onClick={createPlaylist}
                disabled={isCreatingPlaylist || !moodTransition}
                className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-green-300"
              >
                {isCreatingPlaylist ? 'Creating...' : 'Create Spotify Playlist'}
              </button>
            </div>
          ) : (
            <div>
              <p className="mb-3">Your playlist is ready!</p>
              <a 
                href={playlistUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="px-4 py-2 bg-green-500 text-white rounded inline-block hover:bg-green-600"
              >
                Open in Spotify
              </a>
            </div>
          )}
        </div>
      )}
      
      {error && (
        <div className="mt-3 p-2 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default SpotifyIntegration;