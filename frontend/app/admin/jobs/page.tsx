'use client';

import { useState, useEffect } from 'react';
import JobModerationCard from '@/components/features/admin/JobModerationCard';
import { jobsApi } from '@/lib/api';
import { Job } from '@/lib/types';

export default function JobModerationPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await jobsApi.getPending();
        setJobs(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load pending jobs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  const handleApprove = async (id: number) => {
    try {
      await jobsApi.approve(id);
      setJobs(jobs.filter(job => job.id !== id));
    } catch (error) {
      console.error('Error approving job:', error);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await jobsApi.reject(id);
      setJobs(jobs.filter(job => job.id !== id));
    } catch (error) {
      console.error('Error rejecting job:', error);
    }
  };

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (error) {
    return <div className="p-6">Error: {error}</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Job Moderation</h1>
      {jobs.length === 0 ? (
        <p>No pending job postings.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map(job => (
            <JobModerationCard
              key={job.id}
              job={job}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </div>
  );
}
