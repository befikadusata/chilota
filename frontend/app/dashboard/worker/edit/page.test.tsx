import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import EditWorkerProfile from '@/app/dashboard/worker/edit/page';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock the AuthContext
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { role: 'worker' },
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

describe('EditWorkerProfile Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for fetching profile
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        id: 1,
        fayda_id: 'ABC123',
        full_name: 'John Doe',
        age: 25,
        place_of_birth: 'Addis Ababa',
        region_of_origin: 'Addis Ababa',
        current_location: 'Addis Ababa',
        emergency_contact_name: 'Jane Doe',
        emergency_contact_phone: '+251912345678',
        languages: ['Amharic'],
        education_level: 'tertiary',
        religion: 'eth_orthodox',
        working_time: 'full_time',
        skills: ['Cooking'],
        years_experience: 3,
        profile_completeness: 80
      }),
    };
  });

  it('fetches and displays worker profile data', async () => {
    render(<EditWorkerProfile />);
    
    // Wait for profile to load
    await waitFor(() => {
      expect(screen.getByDisplayValue('ABC123')).toBeInTheDocument();
      expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('25')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Addis Ababa')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Jane Doe')).toBeInTheDocument();
      expect(screen.getByDisplayValue('+251912345678')).toBeInTheDocument();
      expect(screen.getByRole('combobox', { value: 'tertiary' })).toBeInTheDocument();
      expect(screen.getByRole('combobox', { value: 'eth_orthodox' })).toBeInTheDocument();
      expect(screen.getByRole('combobox', { value: 'full_time' })).toBeInTheDocument();
      expect(screen.getByDisplayValue('3')).toBeInTheDocument();
    });
  });

  it('validates required fields on submit', async () => {
    render(<EditWorkerProfile />);
    
    // Wait for profile to load
    await waitFor(() => {
      expect(screen.getByText('Edit Worker Profile')).toBeInTheDocument();
    });
    
    // Clear required fields
    fireEvent.change(screen.getByLabelText('Fayda ID'), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: '' } });
    fireEvent.change(screen.getByLabelText('Age'), { target: { value: '' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Profile'));
    
    // Wait for validation errors
    await waitFor(() => {
      expect(screen.getByText('Fayda ID is required')).toBeInTheDocument();
      expect(screen.getByText('Full name is required')).toBeInTheDocument();
      expect(screen.getByText('Age is required')).toBeInTheDocument();
    });
  });

  it('submits updated profile data', async () => {
    // Mock successful update response
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({}),
    };
    
    render(<EditWorkerProfile />);
    
    // Wait for profile to load
    await waitFor(() => {
      expect(screen.getByDisplayValue('ABC123')).toBeInTheDocument();
    });
    
    // Change some values
    fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: 'Jane Smith' } });
    fireEvent.change(screen.getByLabelText('Age'), { target: { value: '30' } });
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Profile'));
    
    // Wait for submission
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workers/',
        expect.objectContaining({
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token',
          },
          body: expect.stringContaining('Jane Smith'),
        })
      );
    });
  });

  it('shows error when update fails', async () => {
    // Mock failed update response
    mockFetchResponse = {
      ok: false,
      json: () => Promise.resolve({ error: 'Failed to update profile' }),
    };
    
    render(<EditWorkerProfile />);
    
    // Wait for profile to load
    await waitFor(() => {
      expect(screen.getByDisplayValue('ABC123')).toBeInTheDocument();
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Update Profile'));
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Failed to update profile')).toBeInTheDocument();
    });
  });
});