import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Handle unauthorized access
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (credentials) => apiClient.post('/auth/login', credentials),
    register: (userData) => apiClient.post('/auth/register', userData),
    logout: () => apiClient.post('/auth/logout'),
    getCurrentUser: () => apiClient.get('/auth/me'),
};

// Applications API
export const applicationsAPI = {
    getAll: (params) => apiClient.get('/applications', { params }),
    getById: (id) => apiClient.get(`/applications/${id}`),
    create: (data) => apiClient.post('/applications', data),
    update: (id, data) => apiClient.put(`/applications/${id}`, data),
    delete: (id) => apiClient.delete(`/applications/${id}`),
    getMetrics: (id) => apiClient.get(`/applications/${id}/metrics`),
};

// Deployments API
export const deploymentsAPI = {
    getAll: (params) => apiClient.get('/deployments', { params }),
    getById: (id) => apiClient.get(`/deployments/${id}`),
    create: (data) => apiClient.post('/deployments', data),
    rollback: (id) => apiClient.post(`/deployments/${id}/rollback`),
    getLogs: (id) => apiClient.get(`/deployments/${id}/logs`),
    getByApplication: (appId) => apiClient.get(`/applications/${appId}/deployments`),
};

// Incidents API
export const incidentsAPI = {
    getAll: (params) => apiClient.get('/incidents', { params }),
    getById: (id) => apiClient.get(`/incidents/${id}`),
    create: (data) => apiClient.post('/incidents', data),
    update: (id, data) => apiClient.put(`/incidents/${id}`, data),
    resolve: (id, resolution) => apiClient.post(`/incidents/${id}/resolve`, resolution),
    addComment: (id, comment) => apiClient.post(`/incidents/${id}/comments`, comment),
};

// Pipelines API
export const pipelinesAPI = {
    getAll: (params) => apiClient.get('/pipelines', { params }),
    getById: (id) => apiClient.get(`/pipelines/${id}`),
    create: (data) => apiClient.post('/pipelines', data),
    trigger: (id) => apiClient.post(`/pipelines/${id}/trigger`),
    cancel: (id) => apiClient.post(`/pipelines/${id}/cancel`),
    getLogs: (id, stageId) => apiClient.get(`/pipelines/${id}/stages/${stageId}/logs`),
};

// Monitoring API
export const monitoringAPI = {
    getMetrics: (params) => apiClient.get('/monitoring/metrics', { params }),
    getHealthStatus: () => apiClient.get('/monitoring/health'),
    getAlerts: (params) => apiClient.get('/monitoring/alerts', { params }),
    getSystemMetrics: () => apiClient.get('/monitoring/system'),
    getApplicationMetrics: (appId, params) => apiClient.get(`/monitoring/applications/${appId}`, { params }),
};

// Settings API
export const settingsAPI = {
    getProfile: () => apiClient.get('/settings/profile'),
    updateProfile: (data) => apiClient.put('/settings/profile', data),
    changePassword: (data) => apiClient.post('/settings/password', data),
    getNotificationSettings: () => apiClient.get('/settings/notifications'),
    updateNotificationSettings: (data) => apiClient.put('/settings/notifications', data),
    getAPIKeys: () => apiClient.get('/settings/api-keys'),
    createAPIKey: (data) => apiClient.post('/settings/api-keys', data),
    revokeAPIKey: (id) => apiClient.delete(`/settings/api-keys/${id}`),
};

// Dashboard API
export const dashboardAPI = {
    getOverview: () => apiClient.get('/dashboard/overview'),
    getRecentActivity: (params) => apiClient.get('/dashboard/activity', { params }),
    getStats: () => apiClient.get('/dashboard/stats'),
};

export default apiClient;
