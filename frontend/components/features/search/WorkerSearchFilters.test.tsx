import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import WorkerSearchFilters from '@/components/features/search/WorkerSearchFilters';

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

describe('WorkerSearchFilters Component', () => {
  const mockOnFilterChange = jest.fn();
  const mockCurrentFilters = {};

  beforeEach(() => {
    // Reset mocks
    mockOnFilterChange.mockClear();
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for filter options
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({
        regions: ['Addis Ababa', 'Oromia', 'Amhara'],
        skills: ['Cooking', 'Cleaning', 'Childcare'],
        languages: ['Amharic', 'English', 'Oromo'],
        education_levels: ['primary', 'secondary', 'tertiary'],
        religions: ['eth_orthodox', 'islam', 'protestant'],
        working_times: ['full_time', 'part_time', 'live_in'],
        experience_range: { min: 0, max: 10 },
        age_range: { min: 18, max: 65 },
        rating_range: { min: 0, max: 5 },
      }),
    };
  });

  it('renders the filter component correctly', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument();
      expect(screen.getByText('Location')).toBeInTheDocument();
      expect(screen.getByText('Skills')).toBeInTheDocument();
      expect(screen.getByText('Languages')).toBeInTheDocument();
      expect(screen.getByText('Reset')).toBeInTheDocument();
    });
  });

  it('loads and displays filter options', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByDisplayValue('Addis Ababa')).toBeInTheDocument();
      expect(screen.getByText('Cooking')).toBeInTheDocument();
      expect(screen.getByText('Amharic')).toBeInTheDocument();
    });
  });

  it('handles location filter changes', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Region of Origin')).toBeInTheDocument();
    });
    
    fireEvent.change(screen.getByPlaceholderText('Region of Origin'), {
      target: { value: 'Addis Ababa' },
    });
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      region_of_origin: 'Addis Ababa',
    });
  });

  it('handles multi-select filter changes', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Cooking')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByLabelText('Cooking'));
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      skills: ['Cooking'],
    });
  });

  it('handles education level filter changes', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Education Level')).toBeInTheDocument();
    });
    
    fireEvent.change(screen.getByRole('combobox', { name: /Education Level/i }), {
      target: { value: 'tertiary' },
    });
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      education_level: 'tertiary',
    });
  });

  it('handles experience range filter changes', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Min')).toBeInTheDocument();
    });
    
    fireEvent.change(screen.getByPlaceholderText('Min'), {
      target: { value: '2' },
    });
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      experience_min: '2',
    });
  });

  it('resets filters when reset button is clicked', async () => {
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Reset')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('Reset'));
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({});
  });

  it('handles error when loading filter options', async () => {
    // Mock an error response
    mockFetchResponse = {
      ok: false,
    };
    
    render(
      <WorkerSearchFilters 
        onFilterChange={mockOnFilterChange} 
        currentFilters={mockCurrentFilters} 
      />
    );
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load filter options')).toBeInTheDocument();
    });
  });
});