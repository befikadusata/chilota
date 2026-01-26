// lib/types/worker.types.ts
import { User } from './user.types';

export interface Worker {
  id: number;
  user_id: number;
  full_name: string;
  profession: string;
  experience_years: number;
  hourly_rate: number;
  hourly_rate_currency: string;
  bio?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  skills: string[];
  languages: string[];
  education?: string;
  certifications: Certification[];
  portfolio?: string;
  availability_status: 'available' | 'busy' | 'unavailable';
  profile_completion_percentage: number;
  rating?: number;
  total_reviews?: number;
  created_at: string;
  updated_at: string;
  avatar?: string;
  is_verified: boolean;
  is_available: boolean;
}

export interface Certification {
  id: number;
  worker_id: number;
  title: string;
  issuer: string;
  issue_date: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkerExperience {
  id: number;
  worker_id: number;
  company: string;
  position: string;
  start_date: string;
  end_date?: string;
  currently_working: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkerEducation {
  id: number;
  worker_id: number;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date: string;
  end_date?: string;
  grade?: string;
  description?: string;
  created_at: string;
  updated_at: string;
}