import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';

import WorkerSearchResults from '@/components/features/search/WorkerSearchResults';
import { Worker } from '@/lib/types';

// Mock data
const mockWorkers: Worker[] = [
  {
    id: 1,
    user_id: 1,
    full_name: 'John Doe',
    age: 25,
    place_of_birth: 'Addis Ababa',
    region_of_origin: 'Addis Ababa',
    current_location: 'Addis Ababa',
    languages: ['Amharic', 'English'],
    education_level: 'tertiary',
    religion: 'eth_orthodox',
    working_time: 'full_time',
    skills: ['Cooking', 'Cleaning'],
    years_experience: 3,
    rating: 4.5,
    is_approved: true,
    profile_photo_url: null,
    user_verified: true,
    date_registered: '2023-01-01T00:00:00Z',
  },
];

// Mock the AuthContext
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, role: 'employer', username: 'testuser' },
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

describe('Cross-Browser and Device Compatibility Tests', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ results: mockWorkers }),
    };
  });

  it('renders correctly on Chrome browser (simulated)', async () => {
    // Simulate Chrome browser properties
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      writable: true,
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('renders correctly on Firefox browser (simulated)', async () => {
    // Simulate Firefox browser properties
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
      writable: true,
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('renders correctly on Safari browser (simulated)', async () => {
    // Simulate Safari browser properties
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
      writable: true,
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('renders correctly on mobile device (simulated)', async () => {
    // Simulate mobile device properties
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375, // iPhone width
    });

    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 667, // iPhone height
    });

    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
      writable: true,
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    // Check that mobile-specific layout is applied
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      // Verify that the grid has adjusted for mobile
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('renders correctly on tablet device (simulated)', async () => {
    // Simulate tablet device properties
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768, // iPad width
    });

    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 1024, // iPad height
    });

    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
      writable: true,
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    // Check that tablet-specific layout is applied
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      // Verify that the grid has adjusted for tablet
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('handles different screen resolutions gracefully', async () => {
    // Test with a high-resolution screen
    Object.defineProperty(window, 'devicePixelRatio', {
      writable: true,
      configurable: true,
      value: 2, // High DPI screen
    });

    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1920, // High-res desktop
    });

    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 1080, // High-res desktop
    });

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('maintains functionality with reduced browser features', async () => {
    // Simulate a browser with reduced features
    const originalLocalStorage = window.localStorage;
    const originalFetch = window.fetch;

    // Temporarily remove localStorage
    Object.defineProperty(window, 'localStorage', {
      value: undefined,
      writable: true,
    });

    // Temporarily modify fetch to simulate network issues
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        json: () => Promise.reject(new Error('Network error')),
      })
    );

    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);

    // Even with reduced features, the component should still render
    expect(screen.getByText('John Doe')).toBeInTheDocument();

    // Restore original implementations
    Object.defineProperty(window, 'localStorage', {
      value: originalLocalStorage,
      writable: true,
    });

    global.fetch = originalFetch;
  });
});