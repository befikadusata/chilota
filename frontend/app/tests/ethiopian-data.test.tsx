import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import CreateWorkerProfile from '@/app/dashboard/worker/create/page'; // Assuming this page has the dropdowns
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock the useAuth hook
jest.mock('@/app/contexts/AuthContext');
const mockUseAuth = useAuth as jest.Mock;

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => 'mock-token'),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  },
  writable: true,
});

// Mock fetch for any API calls
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ id: 1, fayda_id: 'ABC123', profile_completeness: 80 }),
  } as Response)
);

describe('Ethiopian Specific Data Validation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({
      user: { role: 'worker' },
    });
  });

  it('populates Region of Origin dropdown with Ethiopian regions', async () => {
    // Mock the API call for regions if it's dynamic
    (global.fetch as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/api/regions')) { // Assuming a /api/regions endpoint
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([
            { id: 1, name: 'Addis Ababa' },
            { id: 2, name: 'Oromia' },
            { id: 3, name: 'Amhara' },
            { id: 4, name: 'Tigray' },
            // ... more regions
          ]),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    });

    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
      expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    // Check if key Ethiopian regions are present in the dropdown
    // This assumes the regions are loaded into a select or similar element
    const regionSelect = screen.getByLabelText('Region of Origin');
    expect(regionSelect).toHaveTextContent('Addis Ababa');
    expect(regionSelect).toHaveTextContent('Oromia');
    expect(regionSelect).toHaveTextContent('Amhara');
    // Add more assertions for other regions if needed
  });

  it('populates Education Level dropdown with expected values', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
      expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    const educationSelect = screen.getByLabelText('Education Level');
    expect(educationSelect).toHaveTextContent('Primary');
    expect(educationSelect).toHaveTextContent('Secondary');
    expect(educationSelect).toHaveTextContent('Tertiary');
  });

  it('populates Religion dropdown with expected Ethiopian religions', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
      expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    const religionSelect = screen.getByLabelText('Religion');
    expect(religionSelect).toHaveTextContent('Ethiopian Orthodox');
    expect(religionSelect).toHaveTextContent('Islam');
    expect(religionSelect).toHaveTextContent('Protestant');
    // Add more assertions for other religions if needed
  });
});
