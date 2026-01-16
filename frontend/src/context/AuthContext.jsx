/**
 * Authentication Context Provider.
 * 
 * Provides:
 * - Current user state
 * - Login/logout functions
 * - Token management
 * 
 * Usage:
 *   const { user, login, logout } = useAuth();
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          // Fetch current user profile
          const userData = await authAPI.getCurrentUser();
          setUser(userData);
        } catch {
          // Token invalid, clear it
          localStorage.removeItem('token');
          localStorage.removeItem('user');
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  /**
   * Login user and store token.
   */
  const login = async (email, password) => {
    const { access_token } = await authAPI.login({ email, password });
    
    // Store token
    localStorage.setItem('token', access_token);
    
    // Fetch user profile
    const userData = await authAPI.getCurrentUser();
    setUser(userData);
    
    return userData;
  };

  /**
   * Signup new user.
   */
  const signup = async (name, email, password) => {
    const userData = await authAPI.signup({ name, email, password });
    
    // Auto-login after signup
    await login(email, password);
    
    return userData;
  };

  /**
   * Logout user and clear token.
   */
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Custom hook to use auth context.
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};