//-
//- Job Moderation Card Component
//-
import { Button } from '@/components/ui/Button';
import { Job } from '@/lib/types';

interface JobModerationCardProps {
  job: Job;
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
}

export default function JobModerationCard({ job, onApprove, onReject }: JobModerationCardProps) {
  return (
    <div className="bg-card overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <h3 className="text-lg font-medium text-card-foreground">{job.title}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{job.location}</p>
        <p className="mt-2 text-sm text-muted-foreground">{job.description}</p>
      </div>
      <div className="p-5 border-t border-border">
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => onReject(job.id)}>Reject</Button>
          <Button variant="primary" onClick={() => onApprove(job.id)}>Approve</Button>
        </div>
      </div>
    </div>
  );
}
