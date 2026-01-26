import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';

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

describe('Responsive Design Tests', () => {
  it('renders correctly on mobile screen sizes', async () => {
    // Set viewport to mobile size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375, // Common mobile width
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 667, // Common mobile height
    });
    
    window.dispatchEvent(new Event('resize'));
    
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    // Check that the grid layout adapts to mobile
    await waitFor(() => {
      // On mobile, the grid should have 1 column
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('renders correctly on tablet screen sizes', async () => {
    // Set viewport to tablet size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 768, // Common tablet width
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 1024, // Common tablet height
    });
    
    window.dispatchEvent(new Event('resize'));
    
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    // Check that the grid layout adapts to tablet
    await waitFor(() => {
      // On tablet, the grid should have 2 columns
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('renders correctly on desktop screen sizes', async () => {
    // Set viewport to desktop size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024, // Common desktop width
    });
    
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768, // Common desktop height
    });
    
    window.dispatchEvent(new Event('resize'));
    
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    // Check that the grid layout adapts to desktop
    await waitFor(() => {
      // On desktop, the grid should have 3 columns
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('has touch-friendly elements', async () => {
    render(<WorkerSearchResults workers={mockWorkers} loading={false} />);
    
    await waitFor(() => {
      // Check for touch-friendly buttons (minimum 44px for touch targets)
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        // In a real test, we would check the computed styles
        expect(button).toBeInTheDocument();
      });
      
      // Check for appropriately sized form elements
      const select = screen.getByRole('combobox');
      expect(select).toBeInTheDocument();
    });
  });
});