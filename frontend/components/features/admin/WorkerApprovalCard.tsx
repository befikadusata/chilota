//-
//- Worker Approval Card Component
//-
import { Button } from '@/components/ui/Button';

//- This is a placeholder for the worker type.
//- It should be replaced with the actual worker type from the API.
interface Worker {
    id: number;
    name: string;
    profession: string;
    experience: number;
}

interface WorkerApprovalCardProps {
  worker: Worker;
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
}

export default function WorkerApprovalCard({ worker, onApprove, onReject }: WorkerApprovalCardProps) {
  return (
    <div className="bg-card overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <h3 className="text-lg font-medium text-card-foreground">{worker.name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{worker.profession}</p>
        <p className="mt-1 text-sm text-muted-foreground">Experience: {worker.experience} years</p>
      </div>
      <div className="p-5 border-t border-border">
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => onReject(worker.id)}>Reject</Button>
          <Button variant="primary" onClick={() => onApprove(worker.id)}>Approve</Button>
        </div>
      </div>
    </div>
  );
}
