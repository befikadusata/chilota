'use client';

import { useState, useEffect } from 'react';
import UserManagementCard from '@/components/features/admin/UserManagementCard';
import { usersApi } from '@/lib/api';

export default function UserManagementPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const data = await usersApi.getAll();
        setUsers(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load users');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleFlag = async (id: string | number) => {
    try {
      await usersApi.flag(id.toString());
      // Optionally, update the user's status in the local state
    } catch (error) {
      console.error('Error flagging user:', error);
    }
  };

  const handleSuspend = async (id: string | number) => {
    try {
      await usersApi.suspend(id.toString());
      // Optionally, update the user's status in the local state
    } catch (error) {
      console.error('Error suspending user:', error);
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
      <h1 className="text-3xl font-bold mb-6">User Management</h1>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <div className="space-y-4">
          {users.map(user => (
            <UserManagementCard
              key={user.id}
              user={user}
              onFlag={handleFlag}
              onSuspend={handleSuspend}
            />
          ))}
        </div>
      )}
    </div>
  );
}
