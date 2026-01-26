import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WorkerSearch from './page';
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';

// Mock the useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the useAuth hook
jest.mock('@/app/contexts/AuthContext');

const mockUseAuth = useAuth as jest.Mock;

const mockSearchResults = {
  results: [
    {
      id: 1,
      user_id: 101,
      full_name: 'Test Worker 1',
      current_location: 'Addis Ababa',
      average_rating: 4.5,
      years_of_experience: 5,
    },
    {
      id: 2,
      user_id: 102,
      full_name: 'Test Worker 2',
      current_location: 'Gondar',
      average_rating: 4.8,
      years_of_experience: 8,
    },
  ],
};

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve(mockSearchResults),
  })
) as jest.Mock;

describe('WorkerSearch', () => {
  const mockRouter = { push: jest.fn() };
  (useRouter as jest.Mock).mockReturnValue(mockRouter);

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({
        user: { role: 'employer', username: 'testemployer' },
    });
  });

  it('renders the search page correctly', async () => {
    render(
      <AuthProvider>
        <WorkerSearch />
      </AuthProvider>
    );

    await waitFor(() => {
        expect(screen.getByText('Find Your Next Worker')).toBeInTheDocument();
    });

    expect(screen.getByPlaceholderText('Search by name, keyword...')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('performs a search when the search button is clicked', async () => {
    render(
        <AuthProvider>
          <WorkerSearch />
        </AuthProvider>
      );

    await waitFor(() => {
        expect(screen.getByText('Find Your Next Worker')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('Search by name, keyword...'), {
      target: { value: 'test' },
    });
    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/api/workers/search/'), expect.any(Object));
      expect(screen.getByText('Test Worker 1')).toBeInTheDocument();
      expect(screen.getByText('Test Worker 2')).toBeInTheDocument();
    });
  });

  it('redirects to worker profile on "View Profile" click', async () => {
    render(
        <AuthProvider>
          <WorkerSearch />
        </AuthProvider>
      );

    await waitFor(() => {
        expect(screen.getByText('Find Your Next Worker')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Search'));

    await waitFor(() => {
      const viewProfileButtons = screen.getAllByText('View Profile');
      fireEvent.click(viewProfileButtons[0]);
    });
    
    await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/worker/101');
    });
  });
});