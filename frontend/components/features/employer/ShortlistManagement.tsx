'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { workersApi } from '@/lib/api';

import { Worker } from '@/lib/types';

interface ShortlistedWorker {
    id: number;
    worker: Worker;
}

export default function ShortlistManagement() {
  const [shortlist, setShortlist] = useState<ShortlistedWorker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchShortlist = async () => {
      try {
        // Placeholder for actual API call
        // const data = await employersApi.getShortlist();
        // For now, simulating an API call
        const data: any[] = [];
        setShortlist(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load shortlist');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchShortlist();
  }, []);

  if (loading) {
    return <p>Loading shortlist...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  if (shortlist.length === 0) {
    return <p>Your shortlist is empty.</p>
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {shortlist.map((shortlistedWorker) => (
        <div key={shortlistedWorker.id} className="bg-card overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <h3 className="text-lg font-medium text-card-foreground">{shortlistedWorker.worker.name}</h3>
            <p className="mt-1 text-sm text-muted-foreground">{shortlistedWorker.worker.profession}</p>
            <p className="mt-1 text-sm text-muted-foreground">Experience: {shortlistedWorker.worker.experience} years</p>
          </div>
          <div className="p-5 border-t border-border">
            <div className="flex justify-end space-x-2">
              <Button variant="outline">View Profile</Button>
              <Button variant="primary">Contact</Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}