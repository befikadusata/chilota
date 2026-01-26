'use client';

import AuthenticatedLayout from '@/components/layout/AuthenticatedLayout';
import { LayoutDashboard, Users, Briefcase, BarChart, Settings } from 'lucide-react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const adminNavItems = [
    { href: '/admin/dashboard', label: 'Dashboard', icon: <LayoutDashboard className="h-5 w-5" /> },
    { href: '/admin/workers', label: 'Workers', icon: <Users className="h-5 w-5" /> },
    { href: '/admin/jobs', label: 'Jobs', icon: <Briefcase className="h-5 w-5" /> },
    { href: '/admin/users', label: 'Users', icon: <Users className="h-5 w-5" /> },
    { href: '/admin/analytics', label: 'Analytics', icon: <BarChart className="h-5 w-5" /> },
    { href: '/admin/settings', label: 'Settings', icon: <Settings className="h-5 w-5" /> },
  ];

  return (
    <AuthenticatedLayout navItems={adminNavItems} userRole="admin">
      {children}
    </AuthenticatedLayout>
  );
}
