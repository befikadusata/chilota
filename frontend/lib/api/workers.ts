import { apiClient } from './client';
import { Worker } from '@/lib/types/worker.types';

export const workersApi = {
  getAll: async (): Promise<Worker[]> => {
    const response = await apiClient.get<Worker[]>('/workers/');
    return response.data;
  },

  getById: async (id: number): Promise<Worker> => {
    const response = await apiClient.get<Worker>(`/workers/${id}/`);
    return response.data;
  },

  create: async (workerData: Partial<Worker>): Promise<Worker> => {
    const response = await apiClient.post<Worker>('/workers/', workerData);
    return response.data;
  },

  update: async (id: number, workerData: Partial<Worker>): Promise<Worker> => {
    const response = await apiClient.put<Worker>(`/workers/${id}/`, workerData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/workers/${id}/`);
  },

  getPending: async (): Promise<Worker[]> => {
    const response = await apiClient.get<Worker[]>('/admin/workers/pending/');
    return response.data;
  },

  approve: async (workerId: number): Promise<void> => {
    await apiClient.post(`/admin/workers/approve/${workerId}/`);
  },

  reject: async (workerId: number): Promise<void> => {
    await apiClient.post(`/admin/workers/reject/${workerId}/`);
  },

  search: async (filters: Record<string, string | string[]>): Promise<Worker[]> => {
    const response = await apiClient.post<Worker[]>('/workers/search/', filters);
    return response.data;
  },
};