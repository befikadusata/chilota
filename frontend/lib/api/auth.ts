import { apiClient } from './client';
import { User } from '@/lib/types/user.types';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  full_name: string;
  email: string;
  password: string;
  role: 'worker' | 'employer' | 'admin';
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login/', credentials);
    // Store tokens in localStorage
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('refreshToken', response.data.refresh_token);
    return response.data;
  },

  register: async (userData: RegisterData): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/register/', userData);
    // Store tokens in localStorage
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('refreshToken', response.data.refresh_token);
    return response.data;
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout/');
    } finally {
      // Always remove tokens regardless of API response
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    }
  },

  refreshToken: async (): Promise<string> => {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<{ access_token: string }>('/auth/refresh/', {
      refresh_token: refreshToken,
    });

    const newToken = response.data.access_token;
    localStorage.setItem('token', newToken);
    return newToken;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me/');
    return response.data;
  },
};