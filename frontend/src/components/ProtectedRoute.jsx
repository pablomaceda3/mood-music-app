import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { isAuthenticated } from '../services/AuthService';

// Component to protect routes that require authentication
const ProtectedRoute = () => {
  const isLoggedIn = isAuthenticated();
  
  // If not authenticated, redirect to login page
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  
  // If authenticated, render the child routes
  return <Outlet />;
};

export default ProtectedRoute;