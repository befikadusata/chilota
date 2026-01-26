// frontend/app/components/ui/StatusBadge.tsx
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils"; // Assuming a utils file for cn

const statusBadgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        pending: "bg-warning/15 text-warning border border-warning/30",
        approved: "bg-success/15 text-success border border-success/30",
        rejected: "bg-destructive/15 text-destructive border border-destructive/30",
        active: "bg-primary/15 text-primary border border-primary/30",
        inactive: "bg-muted text-muted-foreground border border-border",
        draft: "bg-secondary/50 text-secondary-foreground border border-secondary",
        closed: "bg-muted text-muted-foreground border border-border",
      },
      size: {
        sm: "px-2 py-0.5 text-xs",
        md: "px-2.5 py-0.5 text-xs",
        lg: "px-3 py-1 text-sm",
      },
    },
    defaultVariants: {
      variant: "pending",
      size: "md",
    },
  }
);

export interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof statusBadgeVariants> {
  showDot?: boolean;
}

const StatusBadge = React.forwardRef<HTMLSpanElement, StatusBadgeProps>(
  ({ className, variant, size, showDot = true, children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={cn(statusBadgeVariants({ variant, size, className }))}
        {...props}
      >
        {showDot && (
          <span
            className={cn("h-1.5 w-1.5 rounded-full", {
              "bg-warning": variant === "pending",
              "bg-success": variant === "approved",
              "bg-destructive": variant === "rejected",
              "bg-primary": variant === "active",
              "bg-muted-foreground": variant === "inactive" || variant === "closed",
              "bg-secondary-foreground": variant === "draft",
            })}
          />
        )}
        {children}
      </span>
    );
  }
);
StatusBadge.displayName = "StatusBadge";

export { StatusBadge, statusBadgeVariants };
