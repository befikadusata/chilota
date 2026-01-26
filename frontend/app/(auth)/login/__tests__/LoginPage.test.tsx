import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginPage from '../page';
import { useAuth } from '@/lib/auth/auth-context';
import { login as apiLogin } from '@/lib/api';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock AuthContext
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock api module
jest.mock('@/lib/api', () => ({
  login: jest.fn(),
}));

describe('LoginPage', () => {
  const mockLogin = jest.fn();
  const mockPush = jest.fn();

  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({ login: mockLogin });
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (apiLogin as jest.Mock).mockClear();
    mockLogin.mockClear();
    mockPush.mockClear();
  });

  it('renders the login form', () => {
    render(<AuthProvider><LoginPage /></AuthProvider>);

    expect(screen.getByRole('heading', { name: /Login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
    expect(screen.getByText(/Don't have an account?/i)).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    const mockUserData = { id: '1', email: 'test@example.com', role: 'worker' };
    (apiLogin as jest.Mock).mockResolvedValue(mockUserData);

    render(<AuthProvider><LoginPage /></AuthProvider>);

    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Login/i }));

    await waitFor(() => {
      expect(apiLogin).toHaveBeenCalledWith('test@example.com', 'password123');
      expect(mockLogin).toHaveBeenCalledWith(mockUserData);
      expect(mockPush).toHaveBeenCalledWith('/');
    });
  });

  it('handles failed login', async () => {
    (apiLogin as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {}); // Mock console.error

    render(<AuthProvider><LoginPage /></AuthProvider>);

    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: 'wrong@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/Password/i), {
      target: { value: 'wrongpassword' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Login/i }));

    await waitFor(() => {
      expect(apiLogin).toHaveBeenCalledWith('wrong@example.com', 'wrongpassword');
      expect(mockLogin).not.toHaveBeenCalled();
      expect(mockPush).not.toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalledWith('Login failed:', expect.any(Error));
    });

    consoleErrorSpy.mockRestore(); // Restore console.error
  });
});
