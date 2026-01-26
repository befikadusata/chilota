import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import SearchSuggestions from '@/components/features/search/SearchSuggestions';

// Mock the AuthContext
jest.mock('@/lib/auth/auth-context', () => ({
  useAuth: () => ({
    user: { id: 1, role: 'employer' },
  }),
}));

describe('SearchSuggestions Component', () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    mockOnSelect.mockClear();
  });

  it('renders without suggestions when query is empty', () => {
    render(<SearchSuggestions query="" onSelect={mockOnSelect} />);
    
    expect(screen.queryByText('Loading suggestions...')).not.toBeInTheDocument();
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('shows loading state when fetching suggestions', async () => {
    render(<SearchSuggestions query="test" onSelect={mockOnSelect} />);
    
    // Initially shows loading
    expect(screen.getByText('Loading suggestions...')).toBeInTheDocument();
    
    // Wait for suggestions to load
    await waitFor(() => {
      expect(screen.queryByText('Loading suggestions...')).not.toBeInTheDocument();
    });
  });

  it('displays location suggestions', async () => {
    render(<SearchSuggestions query="addis" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Addis Ababa')).toBeInTheDocument();
    });
    
    expect(screen.getByText('📍')).toBeInTheDocument(); // Location icon
  });

  it('displays skill suggestions', async () => {
    render(<SearchSuggestions query="cook" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Cooking')).toBeInTheDocument();
    });
    
    expect(screen.getByText('🔧')).toBeInTheDocument(); // Skill icon
  });

  it('displays language suggestions', async () => {
    render(<SearchSuggestions query="amhar" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Amharic')).toBeInTheDocument();
    });
    
    expect(screen.getByText('🗣️')).toBeInTheDocument(); // Language icon
  });

  it('calls onSelect when a suggestion is clicked', async () => {
    render(<SearchSuggestions query="addis" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Addis Ababa')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Addis Ababa'));
    
    expect(mockOnSelect).toHaveBeenCalledWith('Addis Ababa');
  });

  it('limits suggestions to 5', async () => {
    render(<SearchSuggestions query="a" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      // Check that we don't have too many suggestions
      const suggestions = screen.getAllByRole('listitem');
      expect(suggestions.length).toBeLessThanOrEqual(5);
    });
  });

  it('hides suggestions when clicking outside', async () => {
    render(<SearchSuggestions query="test" onSelect={mockOnSelect} />);
    
    await waitFor(() => {
      expect(screen.getByText('Loading suggestions...')).not.toBeInTheDocument();
    });
    
    // Simulate clicking outside
    fireEvent.mouseDown(document.body);
    
    // Suggestions should be hidden after a delay
    await waitFor(() => {
      expect(screen.queryByText('Addis Ababa')).not.toBeInTheDocument();
    }, { timeout: 300 });
  });
});