// frontend/app/components/layout/AuthenticatedHeader.tsx
'use client';

import Link from "next/link";
import { Button } from "@/app/components/ui/Button";
import { Bell, LogOut, Settings, User } from "lucide-react";
import { useAuth } from "@/app/contexts/AuthContext";
import { useRouter } from "next/navigation"; // Use next/navigation for Next.js router

export default function AuthenticatedHeader() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login'); // Redirect to login after logout
  };

  const userName = user?.email || "User"; // Placeholder, real user data would be used

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        {/* Logo/Site Title */}
        <Link href={`/${user?.role}/dashboard`} className="text-xl font-bold text-primary">
          SurveAddis
        </Link>

        {/* Right Side Actions */}
        <div className="flex items-center gap-2">
          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
            <span className="sr-only">Notifications</span>
          </Button>

          {/* User Dropdown (Simplified for now, could be a full dropdown menu) */}
          <div className="flex items-center gap-2">
            <Button variant="ghost" className="relative h-9 w-9 rounded-full">
              {/* Placeholder for Avatar */}
              <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
                <User className="h-4 w-4" />
              </div>
            </Button>
            <Button variant="ghost" onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
