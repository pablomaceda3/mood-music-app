import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MoodTransition from './components/MoodTransition';
import ConnectionDebugger from './components/ConnectionDebugger';
import Navigation from './components/Navigation';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';
import { isAuthenticated } from './services/AuthService';

function App() {
  const [showDebugger, setShowDebugger] = React.useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navigation />
        
        <button 
          onClick={() => setShowDebugger(!showDebugger)}
          className="fixed top-20 right-4 bg-gray-200 px-3 py-1 rounded-md text-sm z-50"
        >
          {showDebugger ? 'Hide Debugger' : 'Debug Connection'}
        </button>
        
        {showDebugger && <ConnectionDebugger />}
        
        <div className="flex-grow">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={
              isAuthenticated() ? <Navigate to="/dashboard" /> : <Login />
            } />
            <Route path="/register" element={
              isAuthenticated() ? <Navigate to="/dashboard" /> : <Register />
            } />
            
            {/* Protected routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<MoodTransition />} />
              <Route path="/transitions" element={<MoodTransition showHistory={true} />} />
            </Route>
            
            {/* Default route */}
            <Route path="/" element={
              isAuthenticated() ? <Navigate to="/dashboard" /> : <Navigate to="/login" />
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;