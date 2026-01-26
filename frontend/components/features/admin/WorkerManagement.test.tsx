import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import WorkerManagement from '@/components/features/admin/WorkerManagement';

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

describe('WorkerManagement Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for workers
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        results: [
          {
            id: 1,
            user_id: 101,
            full_name: 'John Doe',
            fayda_id: 'FAYDA123',
            age: 28,
            region_of_origin: 'Addis Ababa',
            current_location: 'Bole',
            education_level: 'tertiary',
            religion: 'eth_orthodox',
            working_time: 'full_time',
            skills: ['Cooking', 'Cleaning'],
            years_experience: 3,
            profile_photo_url: null,
            is_approved: false,
            user_verified: false,
            date_registered: '2023-01-01T00:00:00Z',
          },
          {
            id: 2,
            user_id: 102,
            full_name: 'Jane Smith',
            fayda_id: 'FAYDA124',
            age: 32,
            region_of_origin: 'Oromia',
            current_location: 'Piassa',
            education_level: 'secondary',
            religion: 'islam',
            working_time: 'part_time',
            skills: ['Childcare', 'Elderly Care'],
            years_experience: 5,
            profile_photo_url: 'https://example.com/photo.jpg',
            is_approved: true,
            user_verified: true,
            date_registered: '2023-01-15T00:00:00Z',
          }
        ],
      }),
    };
  });

  it('renders worker management correctly', async () => {
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Worker Management')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Mock a delayed response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockImplementationOnce(() =>
      new Promise(() => {}) // Never resolves to simulate loading
    );
    
    render(<WorkerManagement />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('shows error message when fetching fails', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load workers')).toBeInTheDocument();
    });
  });

  it('shows empty state when no workers exist', async () => {
    // Mock empty response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    };
    
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('No workers found')).toBeInTheDocument();
    });
  });

  it('filters workers by status', async () => {
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    // Change filter to pending
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'pending' } });
    
    // The fetch should be called with the new filter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/admin/workers/?status=pending'),
        expect.objectContaining({
          headers: {
            'Authorization': 'Bearer mock-token',
          },
        })
      );
    });
  });

  it('approves a worker', async () => {
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Approve')).toBeInTheDocument();
    });
    
    // Mock successful approval response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    fireEvent.click(screen.getByText('Approve'));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/workers/1/approve/',
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

  it('rejects a worker', async () => {
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Reject')).toBeInTheDocument();
    });
    
    // Mock successful rejection response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    fireEvent.click(screen.getByText('Reject'));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/workers/1/reject/',
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

  it('displays worker information correctly', async () => {
    render(<WorkerManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('FAYDA123')).toBeInTheDocument();
      expect(screen.getByText('Bole')).toBeInTheDocument();
      expect(screen.getByText('Cooking, Cleaning')).toBeInTheDocument();
      expect(screen.getByText('3 years')).toBeInTheDocument();
    });
  });
});