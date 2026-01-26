// lib/constants/api-endpoints.ts
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login/',
    REGISTER: '/auth/register/',
    LOGOUT: '/auth/logout/',
    REFRESH: '/auth/refresh/',
    ME: '/auth/me/',
    VERIFY: '/auth/verify/',
    FORGOT_PASSWORD: '/auth/password/reset/',
    RESET_PASSWORD: '/auth/password/reset/confirm/',
  },
  
  USERS: {
    BASE: '/users/',
    ME: '/users/me/',
    PROFILE: '/users/profile/',
  },
  
  WORKERS: {
    BASE: '/workers/',
    PENDING: '/admin/workers/pending/',
    APPROVE: (id: number) => `/admin/workers/approve/${id}/`,
    REJECT: (id: number) => `/admin/workers/reject/${id}/`,
    SEARCH: '/workers/search/',
  },
  
  JOBS: {
    BASE: '/jobs/',
    PENDING: '/admin/jobs/pending/',
    APPROVE: (id: number) => `/admin/jobs/approve/${id}/`,
    REJECT: (id: number) => `/admin/jobs/reject/${id}/`,
    BY_EMPLOYER: '/employers/jobs/',
  },
  
  EMPLOYERS: {
    BASE: '/employers/',
    PROFILE: '/employers/profile/',
    JOBS: '/employers/jobs/',
    SHORTLIST: '/employers/shortlist/',
  },
  
  ADMIN: {
    DASHBOARD_STATS: '/admin/analytics/platform/',
    ANALYTICS_TRENDS: '/admin/analytics/trends/',
    USERS: '/admin/users/',
    FLAG_USER: (id: number) => `/admin/users/flag/${id}/`,
    SUSPEND_USER: (id: number) => `/admin/users/suspend/${id}/`,
  },
} as const;