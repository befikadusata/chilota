import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => null),
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

// Mock the AuthContext at the top level
const mockUseAuth = jest.fn();
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => mockUseAuth(),
}));

describe('End-to-End User Journey Tests', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    // Reset AuthContext mock
    mockUseAuth.mockReturnValue({
      user: null,
      login: jest.fn(),
      logout: jest.fn(),
    });
  });

  it('completes the full worker registration journey', async () => {
    // Mock auth context for this specific test
    mockUseAuth.mockReturnValue({
      user: null, // Initially not logged in
      login: jest.fn(),
      logout: jest.fn(),
    });

    // Mock responses for the registration journey
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ id: 1, username: 'testworker', email: 'test@example.com', user_type: 'worker' }),
    };

    // Render the app
    const App = require('@/app/layout').default;
    render(<App />);

    // Navigate to registration
    fireEvent.click(screen.getByText('Register'));
    
    // Fill registration form
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'testworker' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'testpassword123' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'testpassword123' } });
    
    // Select user type as worker
    fireEvent.change(screen.getByLabelText('User Type'), { target: { value: 'worker' } });
    
    // Submit registration
    fireEvent.click(screen.getByText('Register'));
    
    // Wait for registration to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/auth/register/',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('testworker'),
        })
      );
    });
    
    // Mock login response after registration
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({ access: 'mock-token', user_type: 'worker' }),
    };
    
    // Wait for redirect to worker profile creation
    await waitFor(() => {
      expect(screen.getByText('Create Worker Profile')).toBeInTheDocument();
    });
    
    // Fill worker profile form
    fireEvent.change(screen.getByLabelText('Fayda ID'), { target: { value: 'FAYDA123456' } });
    fireEvent.change(screen.getByLabelText('Full Name'), { target: { value: 'Test Worker' } });
    fireEvent.change(screen.getByLabelText('Age'), { target: { value: '28' } });
    fireEvent.change(screen.getByLabelText('Place of Birth'), { target: { value: 'Addis Ababa' } });
    fireEvent.change(screen.getByLabelText('Region of Origin'), { target: { value: 'Addis Ababa' } });
    fireEvent.change(screen.getByLabelText('Current Location'), { target: { value: 'Bole' } });
    fireEvent.change(screen.getByLabelText('Emergency Contact Name'), { target: { value: 'Emergency Contact' } });
    fireEvent.change(screen.getByLabelText('Emergency Contact Phone'), { target: { value: '+251912345678' } });
    
    // Select education level
    fireEvent.change(screen.getByLabelText('Education Level'), { target: { value: 'tertiary' } });
    
    // Select religion
    fireEvent.change(screen.getByLabelText('Religion'), { target: { value: 'eth_orthodox' } });
    
    // Select working time
    fireEvent.change(screen.getByLabelText('Working Time Preference'), { target: { value: 'full_time' } });
    
    // Select years of experience
    fireEvent.change(screen.getByLabelText('Years of Experience'), { target: { value: '3' } });
    
    // Select languages
    fireEvent.click(screen.getByLabelText('Amharic'));
    fireEvent.click(screen.getByLabelText('English'));
    
    // Select skills
    fireEvent.click(screen.getByLabelText('Cooking'));
    fireEvent.click(screen.getByLabelText('Cleaning'));
    
    // Submit profile
    fireEvent.click(screen.getByText('Create Profile'));
    
    // Wait for profile creation
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workers/create/',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('FAYDA123456'),
        })
      );
    });
    
    // Expect to be on the worker dashboard
    await waitFor(() => {
      expect(screen.getByText('Worker Dashboard')).toBeInTheDocument();
    });
  });

  it('completes the full employer job posting journey', async () => {
    // Mock auth context for employer
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: 'employer', username: 'testemployer' },
      login: jest.fn(),
      logout: jest.fn(),
    });

    // Mock responses for the job posting journey
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
            applications: 0,
            shortlisted: 0,
          }
        ],
      }),
    };

    // Render the app with employer context
    const App = require('@/app/layout').default;
    render(<App />);

    // Navigate to employer dashboard
    fireEvent.click(screen.getByText('Employer Dashboard'));
    
    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByText('Employer Dashboard')).toBeInTheDocument();
    });
    
    // Click to post a new job
    fireEvent.click(screen.getByText('Post New Job'));
    
    // Wait for job creation form
    await waitFor(() => {
      expect(screen.getByText('Post a New Job')).toBeInTheDocument();
    });
    
    // Fill job posting form
    fireEvent.change(screen.getByLabelText('Job Title *'), { target: { value: 'Housekeeper' } });
    fireEvent.change(screen.getByLabelText('Location *'), { target: { value: 'Bole, Addis Ababa' } });
    fireEvent.change(screen.getByLabelText('Minimum Salary (ETB) *'), { target: { value: '5000' } });
    fireEvent.change(screen.getByLabelText('Maximum Salary (ETB) *'), { target: { value: '7000' } });
    fireEvent.change(screen.getByLabelText('Minimum Experience (years)'), { target: { value: '2' } });
    
    // Select job type
    fireEvent.change(screen.getByLabelText('Job Type *'), { target: { value: 'housekeeper' } });
    
    // Select working time
    fireEvent.change(screen.getByLabelText('Working Time *'), { target: { value: 'full_time' } });
    
    // Select education level
    fireEvent.change(screen.getByLabelText('Education Level'), { target: { value: 'secondary' } });
    
    // Select preferred religion
    fireEvent.change(screen.getByLabelText('Preferred Religion'), { target: { value: 'eth_orthodox' } });
    
    // Fill job description
    fireEvent.change(screen.getByLabelText('Job Description *'), { target: { value: 'Looking for an experienced housekeeper' } });
    
    // Select required skills
    fireEvent.click(screen.getByLabelText('Cooking'));
    fireEvent.click(screen.getByLabelText('Cleaning'));
    
    // Select preferred languages
    fireEvent.click(screen.getByLabelText('Amharic'));
    fireEvent.click(screen.getByLabelText('English'));
    
    // Submit job posting
    fireEvent.click(screen.getByText('Post Job'));
    
    // Wait for job posting to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/jobs/',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('Housekeeper'),
        })
      );
    });
    
    // Expect to be redirected back to employer dashboard
    await waitFor(() => {
      expect(screen.getByText('Employer Dashboard')).toBeInTheDocument();
    });
    
    // Expect the new job to be listed
    expect(screen.getByText('Housekeeper')).toBeInTheDocument();
  });

  it('completes the admin approval workflow', async () => {
    // Mock auth context for admin
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: 'admin', username: 'adminuser' },
      login: jest.fn(),
      logout: jest.fn(),
    });

    // Mock responses for the admin workflow
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        totalWorkers: 150,
        totalEmployers: 85,
        totalJobs: 200,
        pendingApprovals: 12,
        flaggedAccounts: 5,
      }),
    };

    // Render the app with admin context
    const App = require('@/app/layout').default;
    render(<App />);

    // Navigate to admin dashboard
    fireEvent.click(screen.getByText('Admin Dashboard'));
    
    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByText('Admin Dashboard')).toBeInTheDocument();
    });
    
    // Navigate to worker management
    fireEvent.click(screen.getByText('Worker Management'));
    
    // Wait for worker management to load
    await waitFor(() => {
      expect(screen.getByText('Worker Management')).toBeInTheDocument();
    });
    
    // Mock pending workers response
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
          }
        ],
      }),
    };
    
    // Change filter to show pending approvals
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'pending' } });
    
    // Wait for pending workers to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
    
    // Approve the worker
    fireEvent.click(screen.getByText('Approve'));
    
    // Wait for approval to complete
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/admin/workers/1/approve/',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
    
    // Verify the worker is now approved
    await waitFor(() => {
      expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    });
  });

  it('allows employer to search for workers and shortlist them', async () => {
    // Mock auth context for employer
    mockUseAuth.mockReturnValue({
      user: { id: 1, role: 'employer', username: 'testemployer' },
      login: jest.fn(),
      logout: jest.fn(),
    });

    // Render the app with employer context
    const App = require('@/app/layout').default;
    render(<App />);

    // Mock initial fetch for employer profile
    mockFetchResponse = { ok: true, json: () => Promise.resolve({ company_name: 'Test Company' }) };

    // Navigate to employer dashboard
    fireEvent.click(screen.getByText('Employer Dashboard'));

    await waitFor(() => {
      expect(screen.getByText('Employer Dashboard')).toBeInTheDocument();
    });

    // Click 'Find Workers' button
    fireEvent.click(screen.getByText('Find Workers'));

    // Mock search results
    mockFetchResponse = {
        ok: true,
        json: () => Promise.resolve([
            { id: 1, name: 'Worker One', profession: 'Nanny', experience: 5 },
            { id: 2, name: 'Worker Two', profession: 'Housekeeper', experience: 3 },
        ]),
    };

    await waitFor(() => {
        expect(screen.getByText('Find Workers')).toBeInTheDocument();
    });

    // Simulate search action (e.g., clicking a search button, or typing and pressing enter)
    // Assuming there's a search input and a search button on the search page
    // fireEvent.change(screen.getByPlaceholderText('Search by skill or name'), { target: { value: 'Nanny' } });
    // fireEvent.click(screen.getByText('Search'));

    // Wait for search results to appear
    await waitFor(() => {
        expect(screen.getByText('Worker One')).toBeInTheDocument();
        expect(screen.getByText('Worker Two')).toBeInTheDocument();
    });

    // Mock shortlisting API call
    mockFetchResponse = { ok: true, json: () => Promise.resolve({ message: 'Worker shortlisted' }) };

    // Shortlist 'Worker One' - assuming there's a 'Shortlist' button next to each worker
    fireEvent.click(within(screen.getByText('Worker One').closest('div')!).getByText('Shortlist'));

    await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
            '/api/employers/shortlist/', // Adjust endpoint if needed
            expect.objectContaining({
                method: 'POST',
                body: expect.stringContaining('Worker One'), // Or worker ID
            })
        );
    });

    // Navigate to shortlisted workers
    fireEvent.click(screen.getByText('Shortlisted Workers'));

    // Mock shortlisted workers list
    mockFetchResponse = {
        ok: true,
        json: () => Promise.resolve([
            { id: 1, worker: { id: 1, name: 'Worker One', profession: 'Nanny', experience: 5 } },
        ]),
    };

    await waitFor(() => {
        expect(screen.getByText('Shortlisted Workers')).toBeInTheDocument();
        expect(screen.getByText('Worker One')).toBeInTheDocument();
    });
  });
});