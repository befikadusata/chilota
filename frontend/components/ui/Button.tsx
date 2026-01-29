//-
//- Button Component
//-
import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  icon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'icon';
  asChild?: boolean;
}

export function Button({ variant = 'primary', icon, size = 'md', asChild, ...props }: ButtonProps) {
  const baseClasses = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50";

  const variantClasses = {
    primary: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
    secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/90",
    outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
  };

  const sizeClasses = {
    sm: "h-8 rounded-md px-3 text-xs",
    md: "h-9 px-4 py-2",
    lg: "h-10 rounded-md px-8 text-lg",
    icon: "h-9 w-9",
  };

  const { className, children, ...rest } = props;

  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`;

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      className: buttonClasses,
      ...rest
    } as React.HTMLAttributes<HTMLElement>);
  }

  return (
    <button
      className={buttonClasses}
      {...rest}
    >
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </button>
  );
}