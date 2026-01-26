'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

interface WorkerProfile {
  id: number;
  user_id: number;
  full_name: string;
  fayda_id: string;
  age: number;
  region_of_origin: string;
  current_location: string;
  education_level: string;
  religion: string;
  working_time: string;
  skills: string[];
  years_experience: number;
  profile_photo_url: string | null;
  is_approved: boolean;
  user_verified: boolean;
  date_registered: string;
}

export default function WorkerManagement() {
  const [workers, setWorkers] = useState<WorkerProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

  useEffect(() => {
    const fetchWorkers = async () => {
      try {
        let url = '/api/admin/workers/';
        if (filter === 'pending') url += '?status=pending';
        if (filter === 'approved') url += '?status=approved';
        if (filter === 'rejected') url += '?status=rejected';

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch workers');
        }

        const data = await response.json();
        setWorkers(data.results || []);
      } catch (err) {
        setError('Failed to load workers');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWorkers();
  }, [filter]);

  const handleApprove = async (workerId: number) => {
    try {
      const response = await fetch(`/api/admin/workers/${workerId}/approve/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the worker status in the UI
        setWorkers(workers.map(worker => 
          worker.id === workerId ? { ...worker, is_approved: true } : worker
        ));
      } else {
        throw new Error('Failed to approve worker');
      }
    } catch (err) {
      setError('Failed to approve worker');
      console.error(err);
    }
  };

  const handleReject = async (workerId: number) => {
    try {
      const response = await fetch(`/api/admin/workers/${workerId}/reject/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Update the worker status in the UI
        setWorkers(workers.map(worker => 
          worker.id === workerId ? { ...worker, is_approved: false } : worker
        ));
      } else {
        throw new Error('Failed to reject worker');
      }
    } catch (err) {
      setError('Failed to reject worker');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {error}
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Worker Management</h2>
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="p-2 border border-gray-300 rounded"
          >
            <option value="all">All Workers</option>
            <option value="pending">Pending Approval</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {workers.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-xl font-medium text-gray-900 mb-2">No workers found</h3>
          <p className="text-gray-500">Adjust your filters to find workers</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Worker
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Skills
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Experience
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {workers.map((worker) => (
                <tr key={worker.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10">
                        {worker.profile_photo_url ? (
                          <img className="h-10 w-10 rounded-full" src={worker.profile_photo_url} alt="" />
                        ) : (
                          <div className="bg-gray-200 border-2 border-dashed rounded-xl w-10 h-10" />
                        )}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{worker.full_name}</div>
                        <div className="text-sm text-gray-500">{worker.fayda_id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{worker.current_location}</div>
                    <div className="text-sm text-gray-500">{worker.region_of_origin}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">
                      {worker.skills.join(', ')}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {worker.years_experience} years
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      worker.is_approved 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {worker.is_approved ? 'Approved' : 'Pending'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {!worker.is_approved ? (
                      <div className="flex space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleApprove(worker.id)}
                        >
                          Approve
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleReject(worker.id)}
                        >
                          Reject
                        </Button>
                      </div>
                    ) : (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleReject(worker.id)}
                      >
                        Unapprove
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