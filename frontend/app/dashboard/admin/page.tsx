'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import WorkerManagement from '@/components/features/admin/WorkerManagement';
import JobManagement from '@/components/features/admin/JobManagement';
import UserManagement from '@/components/features/admin/UserManagement';

export default function AdminDashboard() {
  const { user } = useAuth();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'workers' | 'jobs' | 'users'>('workers');
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalWorkers: 0,
    totalEmployers: 0,
    totalJobs: 0,
    pendingApprovals: 0,
    flaggedAccounts: 0,
  });

  // Check if user is authenticated and is an admin
  useEffect(() => {
    if (!user || user.role !== 'admin') {
      router.push('/login');
    } else {
      // Fetch admin stats
      const fetchStats = async () => {
        try {
          const response = await fetch('/api/admin/stats/', {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
          });

          if (response.ok) {
            const data = await response.json();
            setStats(data);
          }
        } catch (error) {
          console.error('Error fetching admin stats:', error);
        } finally {
          setLoading(false);
        }
      };

      fetchStats();
    }
  }, [user, router]);

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (!user || user.role !== 'admin') {
    return <div className="p-6">Access denied. Admins only.</div>;
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <p className="text-muted-foreground">Manage platform operations and user content</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-card-foreground">Total Workers</h3>
          <p className="text-3xl font-bold text-primary">{stats.totalWorkers}</p>
        </div>
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-card-foreground">Total Employers</h3>
          <p className="text-3xl font-bold text-success">{stats.totalEmployers}</p>
        </div>
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-card-foreground">Total Jobs</h3>
          <p className="text-3xl font-bold text-warning">{stats.totalJobs}</p>
        </div>
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-card-foreground">Pending Approvals</h3>
          <p className="text-3xl font-bold text-warning">{stats.pendingApprovals}</p>
        </div>
        <div className="bg-card rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-card-foreground">Flagged Accounts</h3>
          <p className="text-3xl font-bold text-error">{stats.flaggedAccounts}</p>
        </div>
      </div>

      <div className="bg-card rounded-lg shadow">
        <div className="border-b border-border">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('workers')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'workers'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-input'
              }`}
            >
              Worker Management
            </button>
            <button
              onClick={() => setActiveTab('jobs')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'jobs'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-input'
              }`}
            >
              Job Management
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`py-4 px-6 text-center border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-input'
              }`}
            >
              User Management
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'workers' && <WorkerManagement />}
          {activeTab === 'jobs' && <JobManagement />}
          {activeTab === 'users' && <UserManagement />}
        </div>
      </div>
    </div>
  );
}