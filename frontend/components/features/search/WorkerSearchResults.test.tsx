import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import WorkerSearchResults from '@/components/features/search/WorkerSearchResults';
import { Worker } from '@/lib/types';

// Mock data
const mockWorkers: Worker[] = [
  {
    id: 1,
    user_id: 1,
    full_name: 'John Doe',
    age: 25,
    place_of_birth: 'Addis Ababa',
    region_of_origin: 'Addis Ababa',
    current_location: 'Addis Ababa',
    languages: ['Amharic', 'English'],
    education_level: 'tertiary',
    religion: 'eth_orthodox',
    working_time: 'full_time',
    skills: ['Cooking', 'Cleaning'],
    years_experience: 3,
    rating: 4.5,
    is_approved: true,
    profile_photo_url: null,
    user_verified: true,
    date_registered: '2023-01-01T00:00:00Z',
  },
  {
    id: 2,
    user_id: 2,
    full_name: 'Jane Smith',
    age: 30,
    place_of_birth: 'Dire Dawa',
    region_of_origin: 'Dire Dawa',
    current_location: 'Addis Ababa',
    languages: ['Amharic', 'English', 'Oromo'],
    education_level: 'secondary',
    religion: 'islam',
    working_time: 'part_time',
    skills: ['Childcare', 'Elderly Care'],
    years_experience: 5,
    rating: 4.8,
    is_approved: true,
    profile_photo_url: 'https://example.com/photo.jpg',
    user_verified: true,
    date_registered: '2023-02-01T00:00:00Z',
  },
];

describe('WorkerSearchResults Component', () => {
  it('renders the search results correctly', () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    expect(screen.getByText('Showing 2 of 2 workers')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('4.5')).toBeInTheDocument();
    expect(screen.getByText('4.8')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    render(<WorkerSearchResults workers={[]} loading={true} />);
    
    expect(screen.getByRole('status')).toBeInTheDocument(); // The loading spinner
  });

  it('displays no results message when workers array is empty', () => {
    render(<WorkerSearchResults workers={[]} loading={false} />);
    
    expect(screen.getByText('No workers found')).toBeInTheDocument();
    expect(screen.getByText('Try adjusting your search filters')).toBeInTheDocument();
  });

  it('handles sorting changes', () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    const sortSelect = screen.getByRole('combobox');
    fireEvent.change(sortSelect, { target: { value: 'rating' } });
    
    expect(sortSelect).toHaveValue('rating');
  });

  it('renders worker profile cards with correct information', () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    // Check first worker
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('3 years exp')).toBeInTheDocument();
    expect(screen.getByText('Addis Ababa')).toBeInTheDocument();
    expect(screen.getByText('tertiary')).toBeInTheDocument();
    
    // Check second worker
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    expect(screen.getByText('5 years exp')).toBeInTheDocument();
    expect(screen.getByText('4.8')).toBeInTheDocument();
  });

  it('handles pagination', async () => {
    // Create more workers to trigger pagination
    const manyWorkers = Array.from({ length: 15 }, (_, i) => ({
      ...mockWorkers[0],
      id: i + 1,
      full_name: `Worker ${i + 1}`,
    }));
    
    render(<WorkerSearchResults workers={manyWorkers} loading={false} />);
    
    // Check that pagination controls are present
    await waitFor(() => {
      expect(screen.getByText('Previous')).toBeInTheDocument();
      expect(screen.getByText('Next')).toBeInTheDocument();
    });
    
    // Check that we're showing the first 10 workers
    expect(screen.getByText('Worker 1')).toBeInTheDocument();
    expect(screen.queryByText('Worker 11')).not.toBeInTheDocument();
    
    // Click next page
    fireEvent.click(screen.getByText('Next'));
    
    // Check that we're now showing the next set of workers
    await waitFor(() => {
      expect(screen.queryByText('Worker 1')).not.toBeInTheDocument();
      expect(screen.getByText('Worker 11')).toBeInTheDocument();
    });
  });

  it('shows skill tags correctly', () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    expect(screen.getByText('Cooking')).toBeInTheDocument();
    expect(screen.getByText('Cleaning')).toBeInTheDocument();
  });

  it('shows language tags correctly', () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    expect(screen.getByText('Amharic')).toBeInTheDocument();
    expect(screen.getByText('English')).toBeInTheDocument();
  });
});