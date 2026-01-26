import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CreateEmployerProfile from './page';
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';

// Mock the useRouter hook
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock the useAuth hook
jest.mock('@/app/contexts/AuthContext', () => ({
    ...jest.requireActual('@/app/contexts/AuthContext'),
    useAuth: jest.fn(),
}));

const mockUseAuth = useAuth as jest.Mock;

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  })
) as jest.Mock;

describe('CreateEmployerProfile', () => {
  const mockRouter = {
    push: jest.fn(),
  };
  (useRouter as jest.Mock).mockReturnValue(mockRouter);

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAuth.mockReturnValue({
        user: { role: 'employer', username: 'testemployer' },
    });
  });

  it('renders the form correctly', async () => {
    render(
      <AuthProvider>
        <CreateEmployerProfile />
      </AuthProvider>
    );

    await waitFor(() => {
        expect(screen.getByLabelText(/Company Name/i)).toBeInTheDocument();
    });

    expect(screen.getByLabelText(/Industry/i)).toBeInTheDocument();
    expect(screen.getByText('Save and Continue')).toBeInTheDocument();
  });

  it('submits the form with valid data', async () => {
    render(
        <AuthProvider>
          <CreateEmployerProfile />
        </AuthProvider>
      );

    await waitFor(() => {
        expect(screen.getByLabelText(/Company Name/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/Company Name/i), { target: { value: 'Test Corp' } });
    fireEvent.change(screen.getByLabelText(/Location/i), { target: { value: 'Addis Ababa' } });
    fireEvent.change(screen.getByLabelText(/Contact Email/i), { target: { value: 'test@corp.com' } });

    fireEvent.click(screen.getByText('Save and Continue'));

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/employers/profile/', expect.any(Object));
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard/employer');
    });
  });

  it('shows an error message if form submission fails', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Failed to create profile' }),
      })
    );

    render(
        <AuthProvider>
          <CreateEmployerProfile />
        </AuthProvider>
      );

    await waitFor(() => {
        expect(screen.getByLabelText(/Company Name/i)).toBeInTheDocument();
    });

            fireEvent.click(screen.getByText('Save and Continue'));

            

            await waitFor(async () => {

              expect(await screen.findByText('Failed to create profile')).toBeInTheDocument();

            });  });
});