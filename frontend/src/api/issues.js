/**
 * Issue API calls.
 */

import api from './axios';

export const issuesAPI = {
  /**
   * Get issues for a project with filters.
   * @param {number} projectId - Project ID
   * @param {Object} params - {q, status, priority, assignee_id, sort, page, page_size}
   * @returns {Promise} {issues, total, page, page_size}
   */
  getIssues: async (projectId, params = {}) => {
    const response = await api.get(`/projects/${projectId}/issues`, { params });
    return response.data;
  },

  /**
   * Create a new issue.
   * @param {number} projectId - Project ID
   * @param {Object} data - {title, description, priority, assignee_id}
   * @returns {Promise} Created issue
   */
  createIssue: async (projectId, data) => {
    const response = await api.post(`/projects/${projectId}/issues`, data);
    return response.data;
  },

  /**
   * Get single issue details.
   * @param {number} issueId - Issue ID
   * @returns {Promise} Issue details
   */
  getIssue: async (issueId) => {
    const response = await api.get(`/issues/${issueId}`);
    return response.data;
  },

  /**
   * Update an issue.
   * @param {number} issueId - Issue ID
   * @param {Object} data - Fields to update
   * @returns {Promise} Updated issue
   */
  updateIssue: async (issueId, data) => {
    const response = await api.patch(`/issues/${issueId}`, data);
    return response.data;
  },

  /**
   * Delete an issue.
   * @param {number} issueId - Issue ID
   * @returns {Promise}
   */
  deleteIssue: async (issueId) => {
    await api.delete(`/issues/${issueId}`);
  },
};