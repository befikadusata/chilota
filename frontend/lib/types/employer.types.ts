// lib/types/employer.types.ts
import { User } from './user.types';
import { Job } from './job.types';

export interface Employer {
  id: number;
  user_id: number;
  company_name: string;
  business_type?: string;
  industry?: string;
  description?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  website?: string;
  established_year?: number;
  employee_count?: string;
  avatar?: string;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface EmployerJobStats {
  total_jobs_posted: number;
  active_jobs: number;
  filled_jobs: number;
  pending_applications: number;
  accepted_applications: number;
}