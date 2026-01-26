// lib/types/user.types.ts
export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'worker' | 'employer' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfile {
  id: number;
  user_id: number;
  bio?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  avatar?: string;
  created_at: string;
  updated_at: string;
}