'use client';

import { useState, useEffect } from 'react';
import WorkerApprovalCard from '@/components/features/admin/WorkerApprovalCard';
import { workersApi } from '@/lib/api';

export default function WorkerApprovalPage() {
  const [workers, setWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkers = async () => {
      try {
        const data = await workersApi.getPending();
        setWorkers(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load pending workers');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkers();
  }, []);

  const handleApprove = async (id: number) => {
    try {
      await workersApi.approve(id);
      setWorkers(workers.filter(worker => worker.id !== id));
    } catch (error) {
      console.error('Error approving worker:', error);
    }
  };

  const handleReject = async (id: number) => {
    try {
      await workersApi.reject(id);
      setWorkers(workers.filter(worker => worker.id !== id));
    } catch (error) {
      console.error('Error rejecting worker:', error);
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
      <h1 className="text-3xl font-bold mb-6">Worker Approvals</h1>
      {workers.length === 0 ? (
        <p>No pending worker approvals.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workers.map(worker => (
            <WorkerApprovalCard
              key={worker.id}
              worker={worker}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}
    </div>
  );
}
