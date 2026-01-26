// frontend/app/components/ui/LoadingSkeleton.tsx
import * as React from "react";
import { cn } from "@/lib/utils"; // Assuming a utils file for cn

interface LoadingSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  // You can add props for different shapes/sizes of skeletons if needed
}

const LoadingSkeleton = React.forwardRef<HTMLDivElement, LoadingSkeletonProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("animate-pulse rounded-md bg-muted", className)}
        {...props}
      />
    );
  }
);
LoadingSkeleton.displayName = "LoadingSkeleton";

export { LoadingSkeleton };
