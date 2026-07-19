import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const resumeAPI = {
  // Upload và parse CV
  parseResume: async (file, jobDescription) => {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    const response = await api.post('/api/parse-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Lấy lịch sử phân tích
  getHistory: async () => {
    const response = await api.get('/api/history');
    return response.data;
  },
};

export const jobDescriptionAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/api/job-descriptions', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/api/job-descriptions/${id}`);
    return response.data;
  },

  create: async (data) => {
    const response = await api.post('/api/job-descriptions', data);
    return response.data;
  },

  update: async (id, data) => {
    const response = await api.put(`/api/job-descriptions/${id}`, data);
    return response.data;
  },

  duplicate: async (id) => {
    const response = await api.post(`/api/job-descriptions/${id}/duplicate`);
    return response.data;
  },

  archive: async (id) => {
    const response = await api.patch(`/api/job-descriptions/${id}/archive`);
    return response.data;
  },

  markUsed: async (id) => {
    const response = await api.post(`/api/job-descriptions/${id}/use`);
    return response.data;
  },
};

export default api;