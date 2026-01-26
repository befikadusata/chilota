import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CreateWorkerProfile from '@/app/dashboard/worker/create/page';
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
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

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ id: 1, fayda_id: 'ABC123', profile_completeness: 80 }),
  } as Response)
);

describe('CreateWorkerProfile Component', () => {
    const mockRouter = {
        push: jest.fn(),
        back: jest.fn(),
    };
    (useRouter as jest.Mock).mockReturnValue(mockRouter);

    beforeEach(() => {
        jest.clearAllMocks();
        mockUseAuth.mockReturnValue({
            user: { role: 'worker' },
        });
    });

  it('renders the form correctly', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });
    
    expect(screen.getByLabelText('Fayda ID')).toBeInTheDocument();
    expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Age')).toBeInTheDocument();
    expect(screen.getByLabelText('Place of Birth')).toBeInTheDocument();
    expect(screen.getByLabelText('Region of Origin')).toBeInTheDocument();
    expect(screen.getByLabelText('Current Location')).toBeInTheDocument();
    expect(screen.getByLabelText('Emergency Contact Name')).toBeInTheDocument();
    expect(screen.getByLabelText('Emergency Contact Phone')).toBeInTheDocument();
    expect(screen.getByLabelText('Education Level')).toBeInTheDocument();
    expect(screen.getByLabelText('Religion')).toBeInTheDocument();
    expect(screen.getByLabelText('Working Time Preference')).toBeInTheDocument();
    expect(screen.getByLabelText('Years of Experience')).toBeInTheDocument();
    expect(screen.getByText('Languages')).toBeInTheDocument();
    expect(screen.getByText('Skills')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });
    
    // Submit the form without filling any fields
    fireEvent.click(screen.getByText('Create Profile'));
    
    // Wait for validation errors to appear
    await waitFor(() => {
      expect(screen.getByText('Fayda ID is required')).toBeInTheDocument();
      expect(screen.getByText('Full name is required')).toBeInTheDocument();
      expect(screen.getByText('Age is required')).toBeInTheDocument();
      expect(screen.getByText('Place of birth is required')).toBeInTheDocument();
      expect(screen.getByText('Region of birth is required')).toBeInTheDocument();
      expect(screen.getByText('Current location is required')).toBeInTheDocument();
      expect(screen.getByText('Emergency contact name is required')).toBeInTheDocument();
      expect(screen.getByText('Emergency contact phone is required')).toBeInTheDocument();
      expect(screen.getByText('Education level is required')).toBeInTheDocument();
      expect(screen.getByText('Religion is required')).toBeInTheDocument();
      expect(screen.getByText('Working time preference is required')).toBeInTheDocument();
      expect(screen.getByText('Years of experience is required')).toBeInTheDocument();
      expect(screen.getByText('Please select at least one language')).toBeInTheDocument();
      expect(screen.getByText('Please select at least one skill')).toBeInTheDocument();
    });
  });

  it('validates Fayda ID format and length', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });
    
    // Enter invalid Fayda ID - too short
    fireEvent.change(screen.getByLabelText('Fayda ID'), {
      target: { value: 'ABC12' },
    });
    await waitFor(() => {
      expect(screen.getByText('Fayda ID must be 10 alphanumeric characters')).toBeInTheDocument();
    });
    
    // Enter invalid Fayda ID - too long
    fireEvent.change(screen.getByLabelText('Fayda ID'), {
      target: { value: 'ABC123456789' },
    });
    await waitFor(() => {
      expect(screen.getByText('Fayda ID must be 10 alphanumeric characters')).toBeInTheDocument();
    });

    // Enter invalid Fayda ID - contains special characters
    fireEvent.change(screen.getByLabelText('Fayda ID'), {
      target: { value: 'FAYDA-123!' },
    });
    await waitFor(() => {
      expect(screen.getByText('Fayda ID can only contain letters and numbers')).toBeInTheDocument();
    });
    
    // Enter valid Fayda ID - 10 alphanumeric characters
    fireEvent.change(screen.getByLabelText('Fayda ID'), {
      target: { value: 'FAYDA12345' },
    });
    
    await waitFor(() => {
      expect(screen.queryByText('Fayda ID can only contain letters and numbers')).not.toBeInTheDocument();
      expect(screen.queryByText('Fayda ID must be 10 alphanumeric characters')).not.toBeInTheDocument();
    });
  });

  it('validates age range', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);
    
    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    // Enter age below minimum
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '10' },
    });
    
    await waitFor(() => {
      expect(screen.getByText('Age must be between 16 and 65')).toBeInTheDocument();
    });
    
    // Enter age above maximum
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '70' },
    });
    
    await waitFor(() => {
      expect(screen.getByText('Age must be between 16 and 65')).toBeInTheDocument();
    });
    
    // Enter valid age
    fireEvent.change(screen.getByLabelText('Age'), {
      target: { value: '25' },
    });
    
    await waitFor(() => {
      expect(screen.queryByText('Age must be between 16 and 65')).not.toBeInTheDocument();
    });
  });

  it('validates phone number format', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);
    
    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    // Enter invalid phone number
    fireEvent.change(screen.getByLabelText('Emergency Contact Phone'), {
      target: { value: 'invalid-phone' },
    });
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid phone number')).toBeInTheDocument();
    });
    
    // Enter valid phone number
    fireEvent.change(screen.getByLabelText('Emergency Contact Phone'), {
      target: { value: '+251912345678' },
    });
    
    await waitFor(() => {
      expect(screen.queryByText('Please enter a valid phone number')).not.toBeInTheDocument();
    });
  });

  it('allows selection of languages and skills', async () => {
    render(<AuthProvider><CreateWorkerProfile /></AuthProvider>);
    
    await waitFor(() => {
        expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });

    // Select a language
    fireEvent.click(screen.getByLabelText('Amharic'));
    
    // Select a skill
    fireEvent.click(screen.getByLabelText('Cooking'));
    
    // Verify selections
    expect(screen.getByLabelText('Amharic')).toBeChecked();
    expect(screen.getByLabelText('Cooking')).toBeChecked();
  });
});