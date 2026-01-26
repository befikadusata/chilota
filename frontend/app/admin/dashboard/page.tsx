'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import StatCard from '@/components/features/admin/StatCard';
import { analyticsApi } from '@/lib/api';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await analyticsApi.getPlatformStats();
        setStats(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load dashboard stats');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (error) {
    return <div className="p-6">Error: {error}</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <StatCard title="Total Users" value={stats?.total_users ?? 'N/A'} />
        <StatCard title="Total Workers" value={stats?.total_workers ?? 'N/A'} />
        <StatCard title="Total Employers" value={stats?.total_employers ?? 'N/A'} />
      </div>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Management</h2>
          <ul className="space-y-2">
            <li><Link href="/admin/workers" className="text-blue-500 hover:underline">Worker Approvals</Link></li>
            <li><Link href="/admin/jobs" className="text-blue-500 hover:underline">Job Moderation</Link></li>
            <li><Link href="/admin/users" className="text-blue-500 hover:underline">User Management</Link></li>
          </ul>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Analytics</h2>
            <Link href="/admin/analytics" className="text-blue-500 hover:underline">View Analytics</Link>
        </div>
      </div>
    </div>
  );
}
