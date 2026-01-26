'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import JobListings from '@/components/features/employer/JobListings';
import ShortlistManagement from '@/components/features/employer/ShortlistManagement';
import { employersApi } from '@/lib/api';

export default function EmployerDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'jobs' | 'shortlist'>('jobs');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employerProfile, setEmployerProfile] = useState<any>(null);

  // Check if user is authenticated and is an employer
  useEffect(() => {
    if (!user || user.role !== 'employer') {
      router.push('/login');
      return;
    }

    // Fetch employer profile
    const fetchEmployerProfile = async () => {
      try {
        // Using a placeholder API call since we don't have a specific employer profile API yet
        // In a real app, we would have an endpoint like employersApi.getProfile()
        // For now, we'll simulate getting the profile from user info
        setEmployerProfile({ company_name: user.full_name || user.email });
      } catch (err: any) {
        setError(err.message || 'Failed to load employer profile');
        console.error(err);

        if (err.message?.includes('404')) {
          // Employer profile doesn't exist, redirect to create profile
          router.push('/dashboard/employer/create-profile');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchEmployerProfile();
  }, [user, router]);

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (error) {
    return <div className="p-6">Error: {error}</div>;
  }

  if (!user || user.role !== 'employer') {
    return <div className="p-6">Access denied. Employers only.</div>;
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Employer Dashboard</h1>
        <p className="text-muted-foreground">Manage your job postings and find the right workers</p>
      </div>

      <div className="bg-card rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-card-foreground">Welcome, {employerProfile?.company_name || user.full_name || user.email}!</h2>
            <p className="text-muted-foreground">Manage your household staff needs</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={() => router.push('/dashboard/employer/search')}>
              Find Workers
            </Button>
            <Button onClick={() => router.push('/dashboard/employer/create-job')}>
              Post New Job
            </Button>
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg shadow">
        <div className="border-b border-border">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('jobs')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'jobs'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-input'
              }`}
            >
              My Job Postings
            </button>
            <button
              onClick={() => setActiveTab('shortlist')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'shortlist'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-input'
              }`}
            >
              Shortlisted Workers
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'jobs' && <JobListings />}
          {activeTab === 'shortlist' && <ShortlistManagement />}
        </div>
      </div>
    </div>
  );
}