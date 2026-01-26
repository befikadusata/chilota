import { apiClient } from './client';
import { User } from '@/lib/types/user.types';

export const usersApi = {
  getAll: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users/');
    return response.data;
  },

  getById: async (id: number): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${id}/`);
    return response.data;
  },

  create: async (userData: Partial<User>): Promise<User> => {
    const response = await apiClient.post<User>('/users/', userData);
    return response.data;
  },

  update: async (id: number, userData: Partial<User>): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${id}/`, userData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/${id}/`);
  },

  flag: async (userId: number): Promise<void> => {
    await apiClient.post(`/admin/users/flag/${userId}/`);
  },

  suspend: async (userId: number): Promise<void> => {
    await apiClient.post(`/admin/users/suspend/${userId}/`);
  },
};