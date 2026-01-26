import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'h-10 w-full rounded-xl border border-border bg-surface px-3 text-sm text-foreground shadow-sm transition focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none',
        'min-w-0',
        className
      )}
      {...props}
    />
  )
);
Input.displayName = 'Input';
