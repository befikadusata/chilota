import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import JobListings from '@/components/features/employer/JobListings';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
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

describe('JobListings Component', () => {
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
            status: 'active',
            applications: 5,
            shortlisted: 2,
          },
          {
            id: 2,
            title: 'Cook',
            description: 'Experienced cook needed for family',
            location: 'Piassa, Addis Ababa',
            salary: '6000-8000',
            posted_date: '2023-01-15T00:00:00Z',
            status: 'filled',
            applications: 8,
            shortlisted: 3,
          }
        ],
      }),
    };
  });

  it('renders job listings correctly', async () => {
    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('Housekeeper')).toBeInTheDocument();
      expect(screen.getByText('Cook')).toBeInTheDocument();
      expect(screen.getByText('Looking for an experienced housekeeper')).toBeInTheDocument();
      expect(screen.getByText('Bole, Addis Ababa')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Mock a delayed response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockImplementationOnce(() =>
      new Promise(() => {}) // Never resolves to simulate loading
    );
    
    render(<JobListings />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('shows error message when fetching fails', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load job listings')).toBeInTheDocument();
    });
  });

  it('shows empty state when no jobs exist', async () => {
    // Mock empty response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    };
    
    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('No job postings yet')).toBeInTheDocument();
      expect(screen.getByText('Post a Job')).toBeInTheDocument();
    });
  });

  it('navigates to edit job page when edit button is clicked', async () => {
    const mockPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({
        push: mockPush,
      }),
    }));

    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('Edit')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Edit'));
    
    expect(mockPush).toHaveBeenCalledWith('/dashboard/employer/edit-job/1');
  });

  it('navigates to job applications page when view applications button is clicked', async () => {
    const mockPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({
        push: mockPush,
      }),
    }));

    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('View Applications (5)')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('View Applications (5)'));
    
    expect(mockPush).toHaveBeenCalledWith('/dashboard/employer/job/1/applications');
  });

  it('displays correct status badges', async () => {
    render(<JobListings />);
    
    await waitFor(() => {
      expect(screen.getByText('active')).toBeInTheDocument();
      expect(screen.getByText('filled')).toBeInTheDocument();
    });
    
    // Check that active jobs have green badges
    const activeBadge = screen.getByText('active').closest('span');
    expect(activeBadge).toHaveClass('bg-green-100');
    
    // Check that filled jobs have blue badges
    const filledBadge = screen.getByText('filled').closest('span');
    expect(filledBadge).toHaveClass('bg-blue-100');
  });
});