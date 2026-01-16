/**
 * Comment API calls.
 */

import api from './axios';

export const commentsAPI = {
  /**
   * Get all comments for an issue.
   * @param {number} issueId - Issue ID
   * @returns {Promise} Array of comments
   */
  getComments: async (issueId) => {
    const response = await api.get(`/issues/${issueId}/comments`);
    return response.data;
  },

  /**
   * Add a comment to an issue.
   * @param {number} issueId - Issue ID
   * @param {Object} data - {body}
   * @returns {Promise} Created comment
   */
  createComment: async (issueId, data) => {
    const response = await api.post(`/issues/${issueId}/comments`, data);
    return response.data;
  },
};