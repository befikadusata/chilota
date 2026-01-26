import { apiClient } from './client';
import { Job } from '@/lib/types/job.types';

export const jobsApi = {
  getAll: async (): Promise<Job[]> => {
    const response = await apiClient.get<Job[]>('/jobs/');
    return response.data;
  },

  getByEmployer: async (): Promise<Job[]> => {
    const response = await apiClient.get<Job[]>('/employers/jobs/');
    return response.data;
  },

  getById: async (id: number): Promise<Job> => {
    const response = await apiClient.get<Job>(`/jobs/${id}/`);
    return response.data;
  },

  create: async (jobData: Partial<Job>): Promise<Job> => {
    const response = await apiClient.post<Job>('/employers/jobs/', jobData);
    return response.data;
  },

  update: async (id: number, jobData: Partial<Job>): Promise<Job> => {
    const response = await apiClient.put<Job>(`/jobs/${id}/`, jobData);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/jobs/${id}/`);
  },

  getPending: async (): Promise<Job[]> => {
    const response = await apiClient.get<Job[]>('/admin/jobs/pending/');
    return response.data;
  },

  approve: async (jobId: number): Promise<void> => {
    await apiClient.post(`/admin/jobs/approve/${jobId}/`);
  },

  reject: async (jobId: number): Promise<void> => {
    await apiClient.post(`/admin/jobs/reject/${jobId}/`);
  },
};