import React from 'react';
import { render, screen } from '@testing-library/react';

import ProfileCompleteness from '@/components/ui/ProfileCompleteness';

describe('ProfileCompleteness Component', () => {
  it('renders the component with correct completeness percentage', () => {
    render(<ProfileCompleteness completeness={75} />);

    expect(screen.getByText('Profile Completeness')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();

    // Check that the progress bar has the correct width
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '75');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '100');
  });

  it('shows appropriate color based on completeness', () => {
    // Test low completeness (red)
    render(<ProfileCompleteness completeness={30} />);
    const progressBar30 = screen.getByRole('progressbar');
    expect(progressBar30).toHaveClass('bg-red-500');

    // Test medium completeness (yellow)
    render(<ProfileCompleteness completeness={60} />);
    const progressBar60 = screen.getByRole('progressbar');
    expect(progressBar60).toHaveClass('bg-yellow-500');

    // Test high completeness (green)
    render(<ProfileCompleteness completeness={85} />);
    const progressBar85 = screen.getByRole('progressbar');
    expect(progressBar85).toHaveClass('bg-green-500');
  });

  it('shows appropriate message based on completeness', () => {
    // Test low completeness message
    render(<ProfileCompleteness completeness={30} />);
    expect(screen.getByText(/Complete your profile to increase visibility/)).toBeInTheDocument();
    
    // Test high completeness message
    render(<ProfileCompleteness completeness={85} />);
    expect(screen.getByText(/Your profile is complete!/)).toBeInTheDocument();
  });

  it('renders correctly at 0% and 100%', () => {
    // Test 0%
    render(<ProfileCompleteness completeness={0} />);
    expect(screen.getByText('0%')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveStyle('width: 0%');
    
    // Test 100%
    render(<ProfileCompleteness completeness={100} />);
    expect(screen.getByText('100%')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveStyle('width: 100%');
  });
});