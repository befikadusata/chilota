import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CreateJobPosting from '@/app/dashboard/employer/create-job/page';
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
    json: () => Promise.resolve({ id: 1 }),
  })
) as jest.Mock;

describe('CreateJobPosting Component', () => {
    const mockRouter = {
        push: jest.fn(),
    };
    (useRouter as jest.Mock).mockReturnValue(mockRouter);

    beforeEach(() => {
        jest.clearAllMocks();
        mockUseAuth.mockReturnValue({
            user: { id: 1, role: 'employer', username: 'employer1' },
        });
    });

  it('renders the job creation form correctly', async () => {
    render(<AuthProvider><CreateJobPosting /></AuthProvider>);
    
    await waitFor(() => {
        expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    expect(screen.getByLabelText('Job Title *')).toBeInTheDocument();
    expect(screen.getByLabelText('Location *')).toBeInTheDocument();
    expect(screen.getByLabelText('Job Description *')).toBeInTheDocument();
    expect(screen.getByText('Required Skills *')).toBeInTheDocument();
    expect(screen.getByText('Post Job')).toBeInTheDocument();
  });

  it('shows access denied for non-employers', () => {
    mockUseAuth.mockReturnValue({
        user: { id: 1, role: 'worker', username: 'worker1' },
    });

    render(<AuthProvider><CreateJobPosting /></AuthProvider>);
    
    expect(screen.getByText('Access denied. Employers only.')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<AuthProvider><CreateJobPosting /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    // Submit the form without filling any required fields
    fireEvent.click(screen.getByText('Post Job'));
    
    // Form validation should prevent submission, so we don't expect the API call
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('submits job posting successfully', async () => {
    render(<AuthProvider><CreateJobPosting /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    // Fill in required fields
    fireEvent.change(screen.getByLabelText('Job Title *'), {
      target: { value: 'Housekeeper' },
    });
    
    fireEvent.change(screen.getByLabelText('Location *'), {
      target: { value: 'Bole, Addis Ababa' },
    });
    
    fireEvent.change(screen.getByLabelText('Job Description *'), {
      target: { value: 'Looking for an experienced housekeeper' },
    });
    
    fireEvent.change(screen.getByLabelText('Minimum Salary (ETB) *'), {
      target: { value: '5000' },
    });
    
    fireEvent.change(screen.getByLabelText('Maximum Salary (ETB) *'), {
      target: { value: '7000' },
    });
    
    // Select required skills
    fireEvent.click(screen.getByLabelText('Cooking'));
    fireEvent.click(screen.getByLabelText('Cleaning'));
    
    // Submit the form
    fireEvent.click(screen.getByText('Post Job'));
    
    // Wait for the API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/employers/jobs/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token',
          },
          body: expect.stringContaining('Housekeeper'),
        })
      );
    });
    
    // Wait for navigation after successful submission
    await waitFor(() => {
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/employer');
    });
  });

  it('shows error when job creation fails', async () => {
    // Mock a failed response
    (fetch as jest.Mock).mockImplementationOnce(() =>
        Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to create job posting' }),
        })
    );
    
    render(<AuthProvider><CreateJobPosting /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    // Fill in required fields
    fireEvent.change(screen.getByLabelText('Job Title *'), {
      target: { value: 'Housekeeper' },
    });
    
    fireEvent.change(screen.getByLabelText('Location *'), {
      target: { value: 'Bole, Addis Ababa' },
    });
    
    fireEvent.change(screen.getByLabelText('Job Description *'), {
      target: { value: 'Looking for an experienced housekeeper' },
    });
    
    fireEvent.change(screen.getByLabelText('Minimum Salary (ETB) *'), {
      target: { value: '5000' },
    });
    
    fireEvent.change(screen.getByLabelText('Maximum Salary (ETB) *'), {
      target: { value: '7000' },
    });
    
    // Select required skills
    fireEvent.click(screen.getByLabelText('Cooking'));
    fireEvent.click(screen.getByLabelText('Cleaning'));
    
    // Submit the form
    fireEvent.click(screen.getByText('Post Job'));
    
    // Wait for the error message
    await waitFor(() => {
      expect(screen.getByText('Failed to create job posting')).toBeInTheDocument();
    });
  });

  it('allows selection of multiple skills and languages', async () => {
    render(<AuthProvider><CreateJobPosting /></AuthProvider>);

    await waitFor(() => {
        expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    // Select multiple skills
    fireEvent.click(screen.getByLabelText('Cooking'));
    fireEvent.click(screen.getByLabelText('Cleaning'));
    fireEvent.click(screen.getByLabelText('Childcare'));
    
    // Select multiple languages
    fireEvent.click(screen.getByLabelText('Amharic'));
    fireEvent.click(screen.getByLabelText('English'));
    
    // Verify selections
    expect(screen.getByLabelText('Cooking')).toBeChecked();
    expect(screen.getByLabelText('Cleaning')).toBeChecked();
    expect(screen.getByLabelText('Childcare')).toBeChecked();
    expect(screen.getByLabelText('Amharic')).toBeChecked();
    expect(screen.getByLabelText('English')).toBeChecked();
  });
});