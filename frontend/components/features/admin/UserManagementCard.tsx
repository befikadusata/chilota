//-
//- User Management Card Component
//-
import { Button } from '@/components/ui/Button';

//- This is a placeholder for the user type.
//- It should be replaced with the actual user type from the API.
interface User {
    id: number;
    name: string;
    email: string;
    role: string;
    status: string;
}

interface UserManagementCardProps {
  user: User;
  onFlag: (id: number) => void;
  onSuspend: (id: number) => void;
}

export default function UserManagementCard({ user, onFlag, onSuspend }: UserManagementCardProps) {
  return (
    <div className="bg-card overflow-hidden shadow rounded-lg p-5 flex justify-between items-center">
      <div>
        <h3 className="text-lg font-medium text-card-foreground">{user.name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{user.email} - {user.role}</p>
        <p className="mt-1 text-sm text-muted-foreground">Status: {user.status}</p>
      </div>
      <div className="flex space-x-2">
        <Button variant="outline" onClick={() => onFlag(user.id)}>Flag</Button>
        <Button variant="secondary" onClick={() => onSuspend(user.id)}>Suspend</Button>
      </div>
    </div>
  );
}
