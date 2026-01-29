// lib/constants/routes.ts
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PROFILE: '/profile',

  // Auth routes
  AUTH: {
    LOGIN: '/login',
    REGISTER: '/register',
    PASSWORD_RESET: '/password-reset',
    VERIFY_EMAIL: '/verify-email',
  },

  // Dashboard routes
  DASHBOARD: {
    ROOT: '/dashboard',
    WORKER: '/dashboard/worker',
    EMPLOYER: '/dashboard/employer',
    ADMIN: '/dashboard/admin',
  },
  
  // Admin routes
  ADMIN: {
    ROOT: '/admin',
    DASHBOARD: '/admin/dashboard',
    USERS: '/admin/users',
    JOBS: '/admin/jobs',
    WORKERS: '/admin/workers',
    ANALYTICS: '/admin/analytics',
  },
  
  // Worker routes
  WORKER: {
    CREATE_PROFILE: '/dashboard/worker/create',
    EDIT_PROFILE: '/dashboard/worker/edit',
    UPLOAD_PHOTO: '/dashboard/worker/upload-photo',
    UPLOAD_CERTIFICATION: '/dashboard/worker/upload-certification',
  },
  
  // Employer routes
  EMPLOYER: {
    CREATE_JOB: '/dashboard/employer/create-job',
    CREATE_PROFILE: '/dashboard/employer/create-profile',
    SEARCH_WORKERS: '/dashboard/employer/search',
  },
  
  // Search routes
  SEARCH: {
    WORKERS: '/search',
  },
} as const;