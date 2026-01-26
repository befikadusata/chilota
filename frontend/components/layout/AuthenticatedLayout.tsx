// frontend/app/components/layout/AuthenticatedLayout.tsx
'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, LayoutDashboard, Users, Briefcase, Settings } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import AuthenticatedHeader from './AuthenticatedHeader'; // Import the new header component

interface NavItem {
  href: string;
  label: string;
  icon?: React.ReactNode; // Optional icon for nav items
}

interface AuthenticatedLayoutProps {
  navItems: NavItem[];
  children: React.ReactNode;
  userRole: 'worker' | 'employer' | 'admin';
}

export default function AuthenticatedLayout({ navItems, children, userRole }: AuthenticatedLayoutProps) {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Define role-specific styling if needed, otherwise use generic.
  // For now, these are placeholders or direct Tailwind classes.
  const roleColors = {
    worker: "text-primary",
    employer: "text-accent", // Example: employer might use accent
    admin: "text-destructive", // Example: admin might use destructive
  };
  const roleLabels = {
    worker: "Worker",
    employer: "Employer",
    admin: "Admin",
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile sidebar toggle */}
      <div className="md:hidden p-4">
        <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="text-foreground">
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 bg-secondary text-secondary-foreground p-4 transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:relative md:translate-x-0 transition-transform duration-200 ease-in-out`}
      >
        <h1 className="text-2xl font-bold mb-6">SurveAddis {roleLabels[userRole]}</h1>
        <nav>
          <ul>
            {navItems.map(item => (
              <li key={item.href} className="mb-2">
                <Link
                  href={item.href}
                  onClick={() => setIsSidebarOpen(false)} // Close sidebar on nav item click
                  className={`flex items-center gap-2 p-2 rounded-lg ${
                    pathname === item.href ? 'bg-secondary-foreground/20 text-secondary-foreground' : 'hover:bg-secondary-foreground/10'
                  }`}
                >
                  {item.icon && item.icon} {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col md:ml-64"> {/* Adjust ml for sidebar width */}
        <AuthenticatedHeader /> {/* Integrated AuthenticatedHeader */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
