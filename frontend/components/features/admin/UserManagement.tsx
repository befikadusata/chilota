'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

interface User {
  id: number;
  username: string;
  email: string;
  user_type: 'worker' | 'employer' | 'admin';
  phone_number: string;
  is_verified: boolean;
  is_active: boolean;
  date_joined: string;
  last_login: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'workers' | 'employers' | 'admins' | 'flagged'>('all');

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        let url = '/api/admin/users/';
        if (filter === 'workers') url += '?user_type=worker';
        if (filter === 'employers') url += '?user_type=employer';
        if (filter === 'admins') url += '?user_type=admin';
        if (filter === 'flagged') url += '?flagged=true';

        const response = await fetch(url, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch users');
        }

        const data = await response.json();
        setUsers(data.results || []);
      } catch (err) {
        setError('Failed to load users');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [filter]);

  const handleToggleVerification = async (userId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/verify/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_verified: !currentStatus }),
      });

      if (response.ok) {
        // Update the user verification status in the UI
        setUsers(users.map(user => 
          user.id === userId ? { ...user, is_verified: !currentStatus } : user
        ));
      } else {
        throw new Error(`Failed to ${!currentStatus ? 'verify' : 'unverify'} user`);
      }
    } catch (err) {
      setError(`Failed to ${!currentStatus ? 'verify' : 'unverify'} user`);
      console.error(err);
    }
  };

  const handleToggleStatus = async (userId: number, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/status/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (response.ok) {
        // Update the user status in the UI
        setUsers(users.map(user => 
          user.id === userId ? { ...user, is_active: !currentStatus } : user
        ));
      } else {
        throw new Error(`Failed to ${!currentStatus ? 'activate' : 'deactivate'} user`);
      }
    } catch (err) {
      setError(`Failed to ${!currentStatus ? 'activate' : 'deactivate'} user`);
      console.error(err);
    }
  };

  const handleFlag = async (userId: number) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/flag/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // In a real implementation, we would update the flag status
        // For now, we'll just show a success message
        alert('User flagged successfully');
      } else {
        throw new Error('Failed to flag user');
      }
    } catch (err) {
      setError('Failed to flag user');
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
        <h2 className="text-xl font-semibold">User Management</h2>
        <div className="flex space-x-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as any)}
            className="p-2 border border-border rounded"
          >
            <option value="all">All Users</option>
            <option value="workers">Workers</option>
            <option value="employers">Employers</option>
            <option value="admins">Admins</option>
            <option value="flagged">Flagged</option>
          </select>
        </div>
      </div>

      {users.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-xl font-medium text-foreground mb-2">No users found</h3>
          <p className="text-muted-foreground">Adjust your filters to find users</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  User
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Contact
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Verification
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-border">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-foreground">{user.username}</div>
                    <div className="text-sm text-muted-foreground">{user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.user_type === 'worker' 
                        ? 'bg-info/10 text-info' 
                        : user.user_type === 'employer'
                        ? 'bg-success/10 text-success'
                        : 'bg-primary/10 text-primary'
                    }`}>
                      {user.user_type.charAt(0).toUpperCase() + user.user_type.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {user.phone_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active 
                        ? 'bg-success/10 text-success' 
                        : 'bg-error/10 text-error'
                    }`}>
                      {user.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_verified 
                        ? 'bg-success/10 text-success' 
                        : 'bg-warning/10 text-warning'
                    }`}>
                      {user.is_verified ? 'Verified' : 'Unverified'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleToggleVerification(user.id, user.is_verified)}
                      >
                        {user.is_verified ? 'Unverify' : 'Verify'}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleToggleStatus(user.id, user.is_active)}
                      >
                        {user.is_active ? 'Suspend' : 'Activate'}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleFlag(user.id)}
                      >
                        Flag
                      </Button>
                    </div>
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