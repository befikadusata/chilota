// lib/types/notification.types.ts
export interface Notification {
  id: number;
  user_id: number;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'alert';
  is_read: boolean;
  created_at: string;
  updated_at: string;
}