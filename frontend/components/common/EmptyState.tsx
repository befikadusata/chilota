// frontend/app/components/ui/EmptyState.tsx
import * as React from "react";
import { PlusCircle } from "lucide-react"; // Example icon

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  actionButton?: React.ReactNode;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No data found",
  description = "There's nothing to display here yet.",
  icon = <PlusCircle className="h-12 w-12 text-muted-foreground" />,
  actionButton,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-card rounded-lg border border-border">
      <div className="mb-4 text-muted-foreground">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-muted-foreground mb-4 max-w-sm">{description}</p>
      {actionButton && <div className="mt-4">{actionButton}</div>}
    </div>
  );
};

export { EmptyState };