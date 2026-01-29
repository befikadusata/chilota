import axios from 'axios';

// Create an axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await apiClient.post('/auth/refresh/', {
            refresh: refreshToken
          });
          
          if (response.data.access) {
            localStorage.setItem('accessToken', response.data.access);
            originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
            return apiClient(originalRequest);
          }
        }
      } catch (refreshError) {
        // Redirect to login if refresh fails
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API functions
export const login = async (email: string, password: string) => {
  try {
    const response = await apiClient.post('/auth/login/', { email, password });
    const { access, refresh, user } = response.data;
    
    // Store tokens in localStorage
    localStorage.setItem('accessToken', access);
    localStorage.setItem('refreshToken', refresh);
    
    return user;
  } catch (error) {
    throw new Error('Login failed: ' + (error as any).response?.data?.detail || 'Unknown error');
  }
};

export const register = async (fullName: string, email: string, password: string, role: string) => {
  try {
    const response = await apiClient.post('/auth/register/', { 
      full_name: fullName, 
      email, 
      password, 
      role 
    });
    return response.data;
  } catch (error) {
    throw new Error('Registration failed: ' + (error as any).response?.data?.detail || 'Unknown error');
  }
};

// Analytics API functions
export const analyticsApi = {
  getStats: async () => {
    try {
      const response = await apiClient.get('/analytics/stats/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch analytics stats: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getChartData: async () => {
    try {
      const response = await apiClient.get('/analytics/chart-data/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch chart data: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getTrends: async () => {
    try {
      const response = await apiClient.get('/analytics/trends/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch trends: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getPlatformStats: async () => {
    try {
      const response = await apiClient.get('/analytics/platform-stats/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch platform stats: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
};

// Authentication API functions
export const authApi = {
  getCurrentUser: async () => {
    try {
      const response = await apiClient.get('/auth/me/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch current user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  logout: async () => {
    try {
      // Clear tokens from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      return true;
    } catch (error) {
      throw new Error('Logout failed: ' + (error as any).message || 'Unknown error');
    }
  },
};

// Jobs API functions
export const jobsApi = {
  getAllJobs: async () => {
    try {
      const response = await apiClient.get('/jobs/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch jobs: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getJobById: async (jobId: string) => {
    try {
      const response = await apiClient.get(`/jobs/${jobId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  createJob: async (jobData: any) => {
    try {
      const response = await apiClient.post('/jobs/', jobData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to create job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  updateJob: async (jobId: string, jobData: any) => {
    try {
      const response = await apiClient.put(`/jobs/${jobId}/`, jobData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  deleteJob: async (jobId: string) => {
    try {
      const response = await apiClient.delete(`/jobs/${jobId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to delete job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getPending: async () => {
    try {
      const response = await apiClient.get('/jobs/pending/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch pending jobs: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  approve: async (jobId: string) => {
    try {
      const response = await apiClient.post(`/jobs/${jobId}/approve/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to approve job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  reject: async (jobId: string) => {
    try {
      const response = await apiClient.post(`/jobs/${jobId}/reject/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to reject job: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getByEmployer: async (employerId: string) => {
    try {
      const response = await apiClient.get(`/jobs/?employer=${employerId}`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch jobs by employer: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
};

// Users API functions
export const usersApi = {
  getAllUsers: async () => {
    try {
      const response = await apiClient.get('/users/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch users: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getUserById: async (userId: string) => {
    try {
      const response = await apiClient.get(`/users/${userId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  updateUser: async (userId: string, userData: any) => {
    try {
      const response = await apiClient.put(`/users/${userId}/`, userData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  deleteUser: async (userId: string) => {
    try {
      const response = await apiClient.delete(`/users/${userId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to delete user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getAll: async () => {
    try {
      const response = await apiClient.get('/users/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch all users: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  flag: async (userId: string) => {
    try {
      const response = await apiClient.post(`/users/${userId}/flag/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to flag user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  suspend: async (userId: string) => {
    try {
      const response = await apiClient.post(`/users/${userId}/suspend/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to suspend user: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
};

// Workers API functions
export const workersApi = {
  getAllWorkers: async () => {
    try {
      const response = await apiClient.get('/workers/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch workers: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getWorkerById: async (workerId: string) => {
    try {
      const response = await apiClient.get(`/workers/${workerId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch worker: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  createWorkerProfile: async (workerData: any) => {
    try {
      const response = await apiClient.post('/workers/', workerData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to create worker profile: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  updateWorkerProfile: async (workerId: string, workerData: any) => {
    try {
      const response = await apiClient.put(`/workers/${workerId}/`, workerData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update worker profile: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  deleteWorkerProfile: async (workerId: string) => {
    try {
      const response = await apiClient.delete(`/workers/${workerId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to delete worker profile: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getPending: async () => {
    try {
      const response = await apiClient.get('/workers/pending/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch pending workers: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  approve: async (workerId: string) => {
    try {
      const response = await apiClient.post(`/workers/${workerId}/approve/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to approve worker: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  reject: async (workerId: string) => {
    try {
      const response = await apiClient.post(`/workers/${workerId}/reject/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to reject worker: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  search: async (filters: any) => {
    try {
      const response = await apiClient.get('/workers/search/', { params: filters });
      return response.data;
    } catch (error) {
      throw new Error('Failed to search workers: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
};

// Employers API functions
export const employersApi = {
  getAll: async () => {
    try {
      const response = await apiClient.get('/employers/');
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch employers: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  getById: async (employerId: string) => {
    try {
      const response = await apiClient.get(`/employers/${employerId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to fetch employer: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  update: async (employerId: string, employerData: any) => {
    try {
      const response = await apiClient.put(`/employers/${employerId}/`, employerData);
      return response.data;
    } catch (error) {
      throw new Error('Failed to update employer: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
  delete: async (employerId: string) => {
    try {
      const response = await apiClient.delete(`/employers/${employerId}/`);
      return response.data;
    } catch (error) {
      throw new Error('Failed to delete employer: ' + (error as any).response?.data?.detail || 'Unknown error');
    }
  },
};