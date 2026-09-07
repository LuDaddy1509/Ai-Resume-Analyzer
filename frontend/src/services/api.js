import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor — attach auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — handle 401 / token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't retried yet, try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          localStorage.setItem('access_token', data.access_token);
          if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
          }
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          return api(originalRequest);
        } catch {
          // Refresh failed — clear tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      }
    }

    return Promise.reject(error);
  }
);

// ---------- Auth API ----------
export const authAPI = {
  login: (email, password) =>
    api.post('/api/auth/login', { email, password }).then((r) => r.data),

  register: (data) =>
    api.post('/api/auth/register', data).then((r) => r.data),

  me: () => api.get('/api/auth/me').then((r) => r.data),

  refresh: (refreshToken) =>
    api.post('/api/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data),
};

// ---------- Resume API ----------
export const resumeAPI = {
  parseResume: async (file, jobDescription) => {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription) {
      formData.append('job_description', jobDescription);
    }
    const response = await api.post('/api/parse-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
    return response.data;
  },

  getHistory: () => api.get('/api/history').then((r) => r.data),

  exportPDF: (historyId) =>
    api.get(`/api/history/${historyId}/export/pdf`, { responseType: 'blob' }),

  exportExcel: (historyId) =>
    api.get(`/api/history/${historyId}/export/excel`, { responseType: 'blob' }),
};

// ---------- Job Description API ----------
export const jobDescriptionAPI = {
  getAll: (params = {}) =>
    api.get('/api/job-descriptions', { params }).then((r) => r.data),

  getById: (id) =>
    api.get(`/api/job-descriptions/${id}`).then((r) => r.data),

  create: (data) =>
    api.post('/api/job-descriptions', data).then((r) => r.data),

  update: (id, data) =>
    api.put(`/api/job-descriptions/${id}`, data).then((r) => r.data),

  duplicate: (id) =>
    api.post(`/api/job-descriptions/${id}/duplicate`).then((r) => r.data),

  archive: (id) =>
    api.patch(`/api/job-descriptions/${id}/archive`).then((r) => r.data),

  markUsed: (id) =>
    api.post(`/api/job-descriptions/${id}/use`).then((r) => r.data),
};

// ---------- Dashboard API ----------
export const dashboardAPI = {
  getSummary: (params = {}) =>
    api.get('/api/dashboard/summary', { params }).then((r) => r.data),

  getScoreDistribution: (params = {}) =>
    api.get('/api/dashboard/score-distribution', { params }).then((r) => r.data),

  getTopSkills: (params = {}) =>
    api.get('/api/dashboard/top-skills', { params }).then((r) => r.data),
};

// ---------- Health ----------
export const healthAPI = {
  check: () =>
    api.get('/health').then((r) => r.data),
};

// ---------- Resume Optimization API ----------
export const optimizationAPI = {
  optimize: (resumeId, data = {}) =>
    api
      .post('/api/resume-optimization/optimize', { resume_id: resumeId, ...data })
      .then((r) => r.data),

  getByResume: (resumeId) =>
    api.get(`/api/resume-optimization/resume/${resumeId}`).then((r) => r.data),

  getById: (id) =>
    api.get(`/api/resume-optimization/${id}`).then((r) => r.data),

  compare: (id) =>
    api.get(`/api/resume-optimization/${id}/compare`).then((r) => r.data),

  exportPDF: (id) =>
    api.post(`/api/resume-optimization/${id}/export-pdf`, {}, { responseType: 'blob' }),
};

// ---------- Skill Gaps API ----------
export const skillGapAPI = {
  analyze: (analysisId, resumeId) =>
    api
      .post('/api/skill-gaps/analyze', { analysis_id: analysisId, resume_id: resumeId })
      .then((r) => r.data),

  getByAnalysis: (analysisId) =>
    api.get(`/api/skill-gaps/analysis/${analysisId}`).then((r) => r.data),

  getLearningPath: (skillGapId) =>
    api.get(`/api/skill-gaps/${skillGapId}/learning-path`).then((r) => r.data),

  createProgress: (userId, data) =>
    api.post(`/api/skill-gaps/progress?user_id=${userId}`, data).then((r) => r.data),

  getProgress: (userId) =>
    api.get(`/api/skill-gaps/progress/${userId}`).then((r) => r.data),

  updateProgress: (progressId, data) =>
    api.patch(`/api/skill-gaps/progress/${progressId}`, data).then((r) => r.data),
};

export default api;