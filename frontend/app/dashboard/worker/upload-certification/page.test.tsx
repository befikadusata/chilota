import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

import UploadCertification from '@/app/dashboard/worker/upload-certification/page';

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
    user: { role: 'worker' },
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
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
  } as Response)
);

describe('UploadCertification Component', () => {
  it('renders the upload form correctly', () => {
    render(<UploadCertification />);
    
    expect(screen.getByText('Upload Certification')).toBeInTheDocument();
    expect(screen.getByText('Click to upload certification')).toBeInTheDocument();
    expect(screen.getByText('PDF, DOC, DOCX, PNG, JPG up to 10MB')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Upload Certification')).toBeInTheDocument();
  });

  it('validates file type', async () => {
    render(<UploadCertification />);
    
    // Create a mock file with invalid type
    const invalidFile = new File(['(⌐□_□)'], 'test.txt', { type: 'text/plain' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload certification');
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    // Wait for validation error
    await waitFor(() => {
      expect(screen.getByText('Invalid file type. Please upload an image, PDF, or Word document.')).toBeInTheDocument();
    });
  });

  it('validates file size', async () => {
    render(<UploadCertification />);
    
    // Create a mock file that exceeds size limit (10MB)
    const largeFile = new File([new ArrayBuffer(11 * 1024 * 1024)], 'large.pdf', { type: 'application/pdf' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload certification');
    fireEvent.change(fileInput, { target: { files: [largeFile] } });
    
    // Wait for validation error
    await waitFor(() => {
      expect(screen.getByText('File size exceeds 10MB limit')).toBeInTheDocument();
    });
  });

  it('allows valid certification file', async () => {
    render(<UploadCertification />);
    
    // Create a mock valid PDF file
    const validFile = new File(['(⌐□_□)'], 'cert.pdf', { type: 'application/pdf' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload certification');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for file name to appear (no error should be shown)
    await waitFor(() => {
      expect(screen.getByText('Selected: cert.pdf')).toBeInTheDocument();
      expect(screen.queryByText('Invalid file type. Please upload an image, PDF, or Word document.')).not.toBeInTheDocument();
      expect(screen.queryByText('File size exceeds 10MB limit')).not.toBeInTheDocument();
    });
  });

  it('submits valid file', async () => {
    render(<UploadCertification />);
    
    // Create a mock valid PDF file
    const validFile = new File(['(⌐□_□)'], 'cert.pdf', { type: 'application/pdf' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload certification');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for file to be selected
    await waitFor(() => {
      expect(fileInput.files).toHaveLength(1);
    });
    
    // Click upload button
    fireEvent.click(screen.getByText('Upload Certification'));
    
    // Wait for submission
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/workers/certification/',
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
    render(<UploadCertification />);
    
    // Create a mock valid PDF file
    const validFile = new File(['(⌐□_□)'], 'cert.pdf', { type: 'application/pdf' });
    
    // Get the file input and fire change event
    const fileInput = screen.getByLabelText('Click to upload certification');
    fireEvent.change(fileInput, { target: { files: [validFile] } });
    
    // Wait for file to be selected
    await waitFor(() => {
      expect(fileInput.files).toHaveLength(1);
    });
    
    // Click upload button
    fireEvent.click(screen.getByText('Upload Certification'));
    
    // Wait for success message
    await waitFor(() => {
      expect(screen.getByText('Certification uploaded successfully!')).toBeInTheDocument();
    });
  });
});