/**
 * Project API calls.
 */

import api from './axios';

export const projectsAPI = {
  /**
   * Get all projects user belongs to.
   * @returns {Promise} Array of projects
   */
  getProjects: async () => {
    const response = await api.get('/projects');
    return response.data;
  },

  /**
   * Create a new project.
   * @param {Object} data - {name, key, description}
   * @returns {Promise} Created project
   */
  createProject: async (data) => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  /**
   * Get project details with members.
   * @param {number} projectId - Project ID
   * @returns {Promise} Project details
   */
  getProject: async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Add a member to project.
   * @param {number} projectId - Project ID
   * @param {Object} data - {email, role}
   * @returns {Promise} Added member
   */
  addMember: async (projectId, data) => {
    const response = await api.post(`/projects/${projectId}/members`, data);
    return response.data;
  },
};