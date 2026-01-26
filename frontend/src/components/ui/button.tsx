import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

export const buttonVariants = ({
  variant = 'primary',
  size = 'md',
}: {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}) => {
  const base =
    'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-colors shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-60 disabled:pointer-events-none';
  const variants: Record<string, string> = {
    primary: 'bg-primary text-white border border-primary hover:opacity-90',
    secondary: 'bg-surface text-foreground border border-border hover:border-primary hover:bg-muted',
    ghost: 'bg-transparent text-foreground hover:bg-muted',
  };
  const sizes: Record<string, string> = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 text-sm',
    lg: 'h-11 px-5 text-sm',
  };
  return cn(base, variants[variant], sizes[size]);
};

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  )
);
Button.displayName = 'Button';
