'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/auth-context';
import { Button } from '@/components/ui/Button';
import { FileUploadInput } from '@/components/ui/FileUploadInput'; // Import the new component

export default function UploadCertification() {
  const router = useRouter();
  const { user } = useAuth();
  
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('certification', file);

      const response = await fetch('/api/workers/certification/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        setSuccess('Certification uploaded successfully!');
        setTimeout(() => {
          router.push('/dashboard/worker');
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Failed to upload certification');
      }
    } catch (err) {
      setError('An error occurred while uploading the certification');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== 'worker') {
    return <div>Access denied. Workers only.</div>;
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Upload Certification</h1>
      
      {error && <div className="bg-error/10 border border-error/50 text-error px-4 py-3 rounded mb-4">{error}</div>}
      {success && <div className="bg-success/10 border border-success/50 text-success px-4 py-3 rounded mb-4">{success}</div>}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <FileUploadInput
          label="Certification Document"
          onFileChange={setFile}
          allowedFileTypes=".pdf,.doc,.docx,image/*"
          maxFileSizeMB={10}
          loading={loading}
          error={error}
        />
        
        <div className="flex justify-end space-x-4">
          <Button type="button" onClick={() => router.back()} variant="secondary">
            Cancel
          </Button>
          <Button type="submit" disabled={loading || !file}>
            {loading ? 'Uploading...' : 'Upload Certification'}
          </Button>
        </div>
      </form>
    </div>
  );
}