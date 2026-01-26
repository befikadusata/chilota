import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import UploadProfilePhoto from '@/app/dashboard/worker/upload-photo/page';

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock the AuthContext
jest.mock('@/app/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 1, role: 'worker', username: 'worker1' },
  }),
}));

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

// Mock MediaDevices API
Object.defineProperty(navigator, 'mediaDevices', {
  value: {
    getUserMedia: jest.fn().mockResolvedValue({
      getTracks: jest.fn().mockReturnValue([{ stop: jest.fn() }]),
    }),
  },
  writable: true,
});

describe('UploadProfilePhoto Component', () => {
  beforeEach(() => {
    // Reset fetch mock
    (global.fetch as vi.MockedFunction<typeof global.fetch>).mockClear();
    
    // Default mock response for successful upload
    mockFetchResponse = {
      ok: true,
      json: () => Promise.resolve({}),
    };
  });

  it('renders the upload form correctly', () => {
    render(<UploadProfilePhoto />);
    
    expect(screen.getByText('Upload Profile Photo')).toBeInTheDocument();
    expect(screen.getByText('Click to upload profile photo')).toBeInTheDocument();
    expect(screen.getByText('Use Camera')).toBeInTheDocument();
  });

  it('switches to camera mode when Use Camera button is clicked', async () => {
    render(<UploadProfilePhoto />);
    
    const useCameraButton = screen.getByText('Use Camera');
    fireEvent.click(useCameraButton);
    
    // Wait for camera to start
    await waitFor(() => {
      expect(screen.getByText('Switch to Gallery')).toBeInTheDocument();
    });
  });

  it('validates file type', async () => {
    render(<UploadProfilePhoto />);
    
    // Create a mock file with invalid type
    const invalidFile = new File(['(⌐□_□)'], 'test.txt', { type: 'text/plain' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload profile photo');
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    // Wait for validation error
    await waitFor(() => {
      expect(screen.getByText('Please select an image file (JPEG, PNG, etc.)')).toBeInTheDocument();
    });
  });

  it('validates file size', async () => {
    render(<UploadProfilePhoto />);
    
    // Create a mock file that exceeds size limit (5MB)
    const largeFile = new File([new ArrayBuffer(6 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload profile photo');
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    // Wait for validation error
    await waitFor(() => {
      expect(screen.getByText('File size exceeds 5MB limit')).toBeInTheDocument();
    });
  });

  it('allows valid image file', async () => {
    render(<UploadProfilePhoto />);
    
    // Create a mock valid image file
    const validFile = new File(['(⌐□_□)'], 'test.jpg', { type: 'image/jpeg' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload profile photo');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for preview to appear (no error should be shown)
    await waitFor(() => {
      expect(screen.queryByText('Please select an image file (JPEG, PNG, etc.)')).not.toBeInTheDocument();
      expect(screen.queryByText('File size exceeds 5MB limit')).not.toBeInTheDocument();
    });
  });

  it('submits valid file', async () => {
    render(<UploadProfilePhoto />);
    
    // Create a mock valid image file
    const validFile = new File(['(⌐□_□)'], 'test.jpg', { type: 'image/jpeg' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload profile photo');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for file to be selected
    await waitFor(() => {
      expect(fileInput.files).toHaveLength(1);
    });
    
    // Click upload button
    fireEvent.click(screen.getByText('Upload Photo'));
    
    // Wait for submission
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workers/photo/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Authorization': 'Bearer mock-token',
          },
          body: expect.any(FormData),
        })
      );
    });
  });

  it('shows success message on successful upload', async () => {
    render(<UploadProfilePhoto />);
    
    // Create a mock valid image file
    const validFile = new File(['(⌐□_□)'], 'test.jpg', { type: 'image/jpeg' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload profile photo');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for file to be selected
    await waitFor(() => {
      expect(fileInput.files).toHaveLength(1);
    });
    
    // Click upload button
    fireEvent.click(screen.getByText('Upload Photo'));
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText('Profile photo uploaded successfully!')).toBeInTheDocument();
    });
  });

  it('handles camera access error', async () => {
    // Mock camera access error
    const mockGetUserMedia = jest.fn().mockRejectedValue(new Error('Camera access denied'));
    Object.defineProperty(navigator, 'mediaDevices', {
      value: {
        getUserMedia: mockGetUserMedia,
      },
      writable: true,
    });

    render(<UploadProfilePhoto />);
    
    const useCameraButton = screen.getByText('Use Camera');
    fireEvent.click(useCameraButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Could not access camera. Please ensure you have granted permission.')).toBeInTheDocument();
    });
  });
});