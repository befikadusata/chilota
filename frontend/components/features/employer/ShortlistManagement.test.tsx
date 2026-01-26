import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import ShortlistManagement from '@/components/features/employer/ShortlistManagement';

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

describe('ShortlistManagement Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for shortlisted workers
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        results: [
          {
            id: 1,
            worker_id: 101,
            job_id: 201,
            full_name: 'John Doe',
            age: 28,
            skills: ['Cooking', 'Cleaning'],
            rating: 4.5,
            years_experience: 3,
            profile_photo_url: null,
            date_shortlisted: '2023-01-01T00:00:00Z',
          },
          {
            id: 2,
            worker_id: 102,
            job_id: 201,
            full_name: 'Jane Smith',
            age: 32,
            skills: ['Childcare', 'Elderly Care'],
            rating: 4.8,
            years_experience: 5,
            profile_photo_url: 'https://example.com/photo.jpg',
            date_shortlisted: '2023-01-15T00:00:00Z',
          }
        ],
      }),
    };
  });

  it('renders shortlisted workers correctly', async () => {
    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
      expect(screen.getByText('Cooking')).toBeInTheDocument();
      expect(screen.getByText('Childcare')).toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    // Mock a delayed response
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockImplementationOnce(() =>
      new Promise(() => {}) // Never resolves to simulate loading
    );
    
    render(<ShortlistManagement />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('shows error message when fetching fails', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load shortlisted workers')).toBeInTheDocument();
    });
  });

  it('shows empty state when no shortlisted workers exist', async () => {
    // Mock empty response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    };
    
    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('No shortlisted workers yet')).toBeInTheDocument();
      expect(screen.getByText('Find Workers')).toBeInTheDocument();
    });
  });

  it('navigates to worker profile when view profile button is clicked', async () => {
    const mockPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({
        push: mockPush,
      }),
    }));

    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('View Profile')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('View Profile'));
    
    expect(mockPush).toHaveBeenCalledWith('/dashboard/worker/101');
  });

  it('navigates to contact page when contact button is clicked', async () => {
    const mockPush = jest.fn();
    jest.mock('next/navigation', () => ({
      useRouter: () => ({
        push: mockPush,
      }),
    }));

    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('Contact')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Contact'));
    
    expect(mockPush).toHaveBeenCalledWith('/dashboard/messages/new?to=101');
  });

  it('displays worker details correctly', async () => {
    render(<ShortlistManagement />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('4.5')).toBeInTheDocument();
      expect(screen.getByText('3 years exp')).toBeInTheDocument();
      expect(screen.getByText('Cooking')).toBeInTheDocument();
      expect(screen.getByText('Cleaning')).toBeInTheDocument();
    });
  });
});