/**
 * Authentication API calls.
 */

import api from './axios';

export const authAPI = {
  /**
   * Register a new user account.
   * @param {Object} data - {name, email, password}
   * @returns {Promise} User data
   */
  signup: async (data) => {
    const response = await api.post('/auth/signup', data);
    return response.data;
  },

  /**
   * Login with email and password.
   * @param {Object} credentials - {email, password}
   * @returns {Promise} {access_token, token_type}
   */
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  /**
   * Get current user profile.
   * @returns {Promise} User data
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};