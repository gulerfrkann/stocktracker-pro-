import axios, { AxiosInstance, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// API instance
const api: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Bir hata oluştu';
    
    // Don't show error toast for certain endpoints
    const silentEndpoints = ['/auth/verify'];
    const isSilent = silentEndpoints.some(endpoint => 
      error.config?.url?.includes(endpoint)
    );
    
    if (!isSilent && error.response?.status !== 401) {
      toast.error(message);
    }
    
    // Handle 401 unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

export default api;

