import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import UserManagement from '@/components/features/admin/UserManagement';

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

describe('UserManagement Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for users
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        results: [
          {
            id: 1,
            username: 'john_doe',
            email: 'john@example.com',
            user_type: 'worker',
            phone_number: '+251912345678',
            is_verified: false,
            is_active: true,
            date_joined: '2023-01-01T00:00:00Z',
            last_login: '2023-01-15T00:00:00Z',
          },
          {
            id: 2,
            username: 'jane_smith',
            email: 'jane@example.com',
            user_type: 'employer',
            phone_number: '+251987654321',
            is_verified: true,
            is_active: true,
            date_joined: '2023-01-02T00:00:00Z',
            last_login: '2023-01-16T00:00:00Z',
          },
          {
            id: 3,
            username: 'admin_user',
            email: 'admin@example.com',
            user_type: 'admin',
            phone_number: '+251911111111',
            is_verified: true,
            is_active: true,
            date_joined: '2023-01-03T00:00:00Z',
            last_login: '2023-01-17T00:00:00Z',
          }
        ],
      }),
    };
  });

  it('renders user management correctly', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('User Management')).toBeInTheDocument();
      expect(screen.getByText('john_doe')).toBeInTheDocument();
      expect(screen.getByText('jane_smith')).toBeInTheDocument();
      expect(screen.getByText('admin_user')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Mock a delayed response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockImplementationOnce(() =>
      new Promise(() => {}) // Never resolves to simulate loading
    );
    
    render(<UserManagement />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('shows error message when fetching fails', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load users')).toBeInTheDocument();
    });
  });

  it('shows empty state when no users exist', async () => {
    // Mock empty response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    };
    
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('No users found')).toBeInTheDocument();
    });
  });

  it('filters users by type', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('john_doe')).toBeInTheDocument();
    });
    
    // Change filter to employers
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'employers' } });
    
    // The fetch should be called with the new filter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/admin/users/?user_type=employer'),
        expect.objectContaining({
          headers: {
            'Authorization': 'Bearer mock-token',
          },
        })
      );
    });
  });

  it('toggles user verification status', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Unverify')).toBeInTheDocument();
    });
    
    // Mock successful verification toggle response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    fireEvent.click(screen.getByText('Unverify'));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/users/2/verify/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ is_verified: false }),
        })
      );
    });
  });

  it('toggles user active status', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Suspend')).toBeInTheDocument();
    });
    
    // Mock successful status toggle response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    fireEvent.click(screen.getByText('Suspend'));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/users/1/status/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ is_active: false }),
        })
      );
    });
  });

  it('flags a user', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Flag')).toBeInTheDocument();
    });
    
    // Mock successful flag response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    // Mock alert function
    window.alert = jest.fn();
    
    fireEvent.click(screen.getByText('Flag'));
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('User flagged successfully');
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/users/1/flag/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
        })
      );
    });
  });

  it('displays user information correctly', async () => {
    render(<UserManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('john_doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('+251912345678')).toBeInTheDocument();
      expect(screen.getByText('Worker')).toBeInTheDocument();
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('Unverified')).toBeInTheDocument();
    });
  });
});