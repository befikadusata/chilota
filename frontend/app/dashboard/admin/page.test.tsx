import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import AdminDashboard from '@/app/dashboard/admin/page';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock the AuthContext
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, role: 'admin', username: 'admin1' },
  }),
}));

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => 'mock-token'),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  },
  writable: true,
});

// Mock fetch
let mockFetchResponse: any;
global.fetch = jest.fn(() =>
  Promise.resolve(mockFetchResponse)
);

describe('AdminDashboard Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for admin stats
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        totalWorkers: 150,
        totalEmployers: 85,
        totalJobs: 200,
        pendingApprovals: 12,
        flaggedAccounts: 5,
      }),
    };
  });

  it('renders the admin dashboard correctly', async () => {
    render(<AdminDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Manage platform operations and user content')).toBeInTheDocument();
    });
  });

  it('shows access denied for non-admins', async () => {
    // Mock a non-admin user
    jest.mock('@/app/contexts/AuthContext', () => ({
      useAuth: () => ({
        user: { id: 1, role: 'worker', username: 'worker1' },
      }),
    }));

    render(<AdminDashboard />);
    
    expect(screen.getByText('Access denied. Admins only.')).toBeInTheDocument();
  });

  it('displays admin statistics', async () => {
    render(<AdminDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument(); // Total Workers
      expect(screen.getByText('85')).toBeInTheDocument();  // Total Employers
      expect(screen.getByText('200')).toBeInTheDocument(); // Total Jobs
      expect(screen.getByText('12')).toBeInTheDocument();  // Pending Approvals
      expect(screen.getByText('5')).toBeInTheDocument();   // Flagged Accounts
    });
  });

  it('switches between management tabs', async () => {
    render(<AdminDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Worker Management')).toBeInTheDocument();
    });
    
    // Switch to job management tab
    fireEvent.click(screen.getByText('Job Management'));
    
    expect(screen.getByText('Job Management')).toBeInTheDocument();
    
    // Switch to user management tab
    fireEvent.click(screen.getByText('User Management'));
    
    expect(screen.getByText('User Management')).toBeInTheDocument();
  });

  it('handles error when fetching stats', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<AdminDashboard />);
    
    // Should still render the dashboard but with default values
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });
  });
});