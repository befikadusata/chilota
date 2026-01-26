import { apiClient } from './client';

export const analyticsApi = {
  getPlatformStats: async (): Promise<any> => {
    const response = await apiClient.get('/admin/analytics/platform/');
    return response.data;
  },

  getTrends: async (): Promise<any> => {
    const response = await apiClient.get('/admin/analytics/trends/');
    return response.data;
  },
};