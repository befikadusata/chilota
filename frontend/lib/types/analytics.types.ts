// lib/types/analytics.types.ts
export interface PlatformStats {
  total_users: number;
  total_workers: number;
  total_employers: number;
  total_jobs: number;
  active_jobs: number;
  filled_jobs: number;
  total_applications: number;
  accepted_applications: number;
  active_workers: number;
  verified_workers: number;
  verified_employers: number;
}

export interface TrendDataPoint {
  date: string;
  value: number;
}

export interface AnalyticsData {
  platform_stats: PlatformStats;
  user_growth: TrendDataPoint[];
  job_postings: TrendDataPoint[];
  applications: TrendDataPoint[];
  top_skills: { skill: string; count: number }[];
  top_professions: { profession: string; count: number }[];
}