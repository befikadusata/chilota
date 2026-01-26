import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';

// Mock the AuthContext as it might be used in the layout or main components
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null, // Or any default mock user state
    login: jest.fn(),
    logout: jest.fn(),
  }),
}));

// Mock the router for any navigation that might occur
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

describe('Ethiopian Context and Cultural Testing - i18n', () => {
  it('renders Amharic text correctly on the homepage', async () => {
    // Dynamically import the App component after mocks are set up
    const App = require('@/app/layout').default;
    render(<App />);

    // Assuming the homepage displays "ሰላም! Welcome to SurveAddis"
    // We specifically check for the Amharic part
    await waitFor(() => {
      expect(screen.getByText('ሰላም!')).toBeInTheDocument();
    });

    // You might also check for the presence of Noto Sans Ethiopic font if you have a way to assert styles
    // This is more complex and usually done with visual regression tests.
  });

  // Add more tests for other components that display Amharic text
  // For example, if there's a worker profile with Amharic labels
  // it('renders Amharic labels on worker profile', async () => {
  //   // Mock appropriate data
  //   // render(<WorkerProfilePage />);
  //   // await waitFor(() => {
  //   //   expect(screen.getByText('የስራ ልምድ')).toBeInTheDocument(); // Amharic for "Experience"
  //   // });
  // });
});
