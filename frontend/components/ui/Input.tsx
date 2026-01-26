import React from 'react';
import { Label } from './Label';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, name, ...props }, ref) => {
    return (
      <div className="grid w-full max-w-sm items-center gap-1.5">
        {label && <Label htmlFor={name}>{label}</Label>}
        <input
            className={`flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
            ref={ref}
            name={name}
            id={name}
            {...props}
        />
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
