// lib/auth/auth-context.tsx
'use client';

import React, {
  createContext,
  useState,
  useContext,
  ReactNode,
  useEffect,
} from 'react';
import { User } from '@/lib/types/user.types';
import { authApi } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (full_name: string, email: string, password: string, role: 'worker' | 'employer' | 'admin') => Promise<void>;
  logout: () => void;
  initializeAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initialize auth state on mount
  useEffect(() => {
    const initAuth = async () => {
      await initializeAuth();
      setIsLoading(false);
    };
    
    initAuth();
  }, []);

  const initializeAuth = async () => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      try {
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      } catch (error) {
        // Token might be invalid/expired, clear it
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        setToken(null);
        setUser(null);
      }
    } else {
      setToken(null);
      setUser(null);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const { user: userData, access_token } = await authApi.login({ email, password });
      setUser(userData);
      setToken(access_token);
    } catch (error) {
      throw error;
    }
  };

  const register = async (full_name: string, email: string, password: string, role: 'worker' | 'employer' | 'admin') => {
    try {
      const { user: userData, access_token } = await authApi.register({ full_name, email, password, role });
      setUser(userData);
      setToken(access_token);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    authApi.logout(); // Call API to invalidate token on server if needed
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      isLoading,
      login, 
      register, 
      logout,
      initializeAuth
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};