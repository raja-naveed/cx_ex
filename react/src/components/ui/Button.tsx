import React from 'react'
import { cn } from '../../lib/utils'
import { Loader2 } from 'lucide-react'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  children: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading = false, disabled, children, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'
    
    const variants = {
      primary: 'bg-emerald-500 text-black font-semibold hover:bg-emerald-400 focus:ring-2 focus:ring-emerald-300 active:scale-[0.98] transition-all duration-200',
      secondary: 'border border-gray-700 bg-gray-900 text-white hover:bg-gray-800 focus:ring-2 focus:ring-emerald-300 active:scale-[0.98] transition-all duration-200',
      ghost: 'text-gray-300 hover:bg-gray-800 hover:text-white focus:ring-2 focus:ring-emerald-300 active:scale-[0.98] transition-all duration-200',
      destructive: 'bg-red-600 text-white hover:bg-red-500 focus:ring-2 focus:ring-red-300 active:scale-[0.98] transition-all duration-200',
    }
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-sm',
      lg: 'px-6 py-3 text-base',
    }

    return (
      <button
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || loading}
        ref={ref}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button }
