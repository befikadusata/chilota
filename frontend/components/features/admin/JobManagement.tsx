'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

interface JobPosting {
  id: number;
  title: string;
  description: string;
  location: string;
  salary: string;
  posted_date: string;
  status: 'active' | 'inactive' | 'filled' | 'pending_approval';
  employer: {
    id: number;
    company_name: string;
  };
  applications: number;
}

export default function JobManagement() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'active' | 'inactive' | 'filled'>('all');

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        let url = '/api/admin/jobs/';
        if (filter === 'pending') url += '?status=pending_approval';
        if (filter === 'active') url += '?status=active';
        if (filter === 'inactive') url += '?status=inactive';
        if (filter === 'filled') url += '?status=filled';

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch jobs');
        }

        const data = await response.json();
        setJobs(data.results || []);
      } catch (err) {
        setError('Failed to load jobs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [filter]);

  const handleApprove = async (jobId: number) => {
    try {
      const response = await fetch(`/api/admin/jobs/${jobId}/approve/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the job status in the UI
        setJobs(jobs.map(job => 
          job.id === jobId ? { ...job, status: 'active' as const } : job
        ));
      } else {
        throw new Error('Failed to approve job');
      }
    } catch (err) {
      setError('Failed to approve job');
      console.error(err);
    }
  };

  const handleReject = async (jobId: number) => {
    try {
      const response = await fetch(`/api/admin/jobs/${jobId}/reject/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the job status in the UI
        setJobs(jobs.map(job => 
          job.id === jobId ? { ...job, status: 'inactive' as const } : job
        ));
      } else {
        throw new Error('Failed to reject job');
      }
    } catch (err) {
      setError('Failed to reject job');
      console.error(err);
    }
  };

  const handleToggleStatus = async (jobId: number, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      const response = await fetch(`/api/admin/jobs/${jobId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        // Update the job status in the UI
        setJobs(jobs.map(job => 
          job.id === jobId ? { ...job, status: newStatus as any } : job
        ));
      } else {
        throw new Error(`Failed to ${newStatus === 'active' ? 'activate' : 'deactivate'} job`);
      }
    } catch (err) {
      setError(`Failed to ${currentStatus === 'active' ? 'activate' : 'deactivate'} job`);
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-error/10 border border-error/50 text-error px-4 py-3 rounded mb-4">
        {error}
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Job Management</h2>
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="p-2 border border-border rounded"
          >
            <option value="all">All Jobs</option>
            <option value="pending">Pending Approval</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="filled">Filled</option>
          </select>
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-xl font-medium text-foreground mb-2">No jobs found</h3>
          <p className="text-muted-foreground">Adjust your filters to find jobs</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Job
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Employer
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Location
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Salary
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Applications
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-border">
              {jobs.map((job) => (
                <tr key={job.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-foreground">{job.title}</div>
                    <div className="text-sm text-muted-foreground line-clamp-2">{job.description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-foreground">{job.employer.company_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {job.location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {job.salary}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      job.status === 'active' 
                        ? 'bg-success/10 text-success' 
                        : job.status === 'inactive'
                        ? 'bg-muted text-muted-foreground'
                        : job.status === 'filled'
                        ? 'bg-info/10 text-info'
                        : 'bg-warning/10 text-warning'
                    }`}>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {job.applications}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {job.status === 'pending_approval' ? (
                      <div className="flex space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleApprove(job.id)}
                        >
                          Approve
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleReject(job.id)}
                        >
                          Reject
                        </Button>
                      </div>
                    ) : (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleToggleStatus(job.id, job.status)}
                      >
                        {job.status === 'active' ? 'Deactivate' : 'Activate'}
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}