import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import JobManagement from '@/components/features/admin/JobManagement';

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

describe('JobManagement Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for jobs
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        results: [
          {
            id: 1,
            title: 'Housekeeper',
            description: 'Looking for an experienced housekeeper',
            location: 'Bole, Addis Ababa',
            salary: '5000-7000',
            posted_date: '2023-01-01T00:00:00Z',
            status: 'pending_approval',
            employer: {
              id: 201,
              company_name: 'ABC Company',
            },
            applications: 5,
          },
          {
            id: 2,
            title: 'Cook',
            description: 'Experienced cook needed for family',
            location: 'Piassa, Addis Ababa',
            salary: '6000-8000',
            posted_date: '2023-01-15T00:00:00Z',
            status: 'active',
            employer: {
              id: 202,
              company_name: 'XYZ Company',
            },
            applications: 8,
          }
        ],
      }),
    };
  });

  it('renders job management correctly', async () => {
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Job Management')).toBeInTheDocument();
      expect(screen.getByText('Housekeeper')).toBeInTheDocument();
      expect(screen.getByText('Cook')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Mock a delayed response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockImplementationOnce(() =>
      new Promise(() => {}) // Never resolves to simulate loading
    );
    
    render(<JobManagement />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('shows error message when fetching fails', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load jobs')).toBeInTheDocument();
    });
  });

  it('shows empty state when no jobs exist', async () => {
    // Mock empty response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    };
    
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });
  });

  it('filters jobs by status', async () => {
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Housekeeper')).toBeInTheDocument();
    });
    
    // Change filter to active
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'active' } });
    
    // The fetch should be called with the new filter
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/admin/jobs/?status=active'),
        expect.objectContaining({
          headers: {
            'Authorization': 'Bearer mock-token',
          },
        })
      );
    });
  });

  it('approves a job', async () => {
    render(<JobManagement />);
    
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
        '/api/admin/jobs/1/approve/',
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

  it('rejects a job', async () => {
    render(<JobManagement />);
    
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
        '/api/admin/jobs/1/reject/',
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

  it('toggles job status', async () => {
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Deactivate')).toBeInTheDocument();
    });
    
    // Mock successful status toggle response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockResolvedValueOnce({
      ok: true,
    });
    
    fireEvent.click(screen.getByText('Deactivate'));
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/jobs/2/',
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: 'inactive' }),
        })
      );
    });
  });

  it('displays job information correctly', async () => {
    render(<JobManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Housekeeper')).toBeInTheDocument();
      expect(screen.getByText('Looking for an experienced housekeeper')).toBeInTheDocument();
      expect(screen.getByText('Bole, Addis Ababa')).toBeInTheDocument();
      expect(screen.getByText('ABC Company')).toBeInTheDocument();
      expect(screen.getByText('5000-7000')).toBeInTheDocument();
      expect(screen.getByText('5')).toBeInTheDocument();
    });
  });
});