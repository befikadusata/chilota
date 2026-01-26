// lib/types/job.types.ts
import { User } from './user.types';

export interface Job {
  id: number;
  title: string;
  description: string;
  location: string;
  salary: number;
  salary_currency: string;
  employment_type: 'full_time' | 'part_time' | 'contract' | 'temporary' | 'internship';
  experience_level: 'entry' | 'mid' | 'senior' | 'executive';
  posted_by: number; // User ID
  skills_required: string[];
  languages_required: string[];
  benefits?: string[];
  requirements: string[];
  responsibilities: string[];
  status: 'draft' | 'active' | 'paused' | 'filled' | 'cancelled';
  created_at: string;
  updated_at: string;
  expires_at?: string;
  applications_count: number;
  employer: User;
}

export interface JobApplication {
  id: number;
  job_id: number;
  worker_id: number;
  cover_letter?: string;
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn';
  applied_at: string;
  updated_at: string;
}