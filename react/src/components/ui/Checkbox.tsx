import React from 'react'
import { cn } from '../../lib/utils'
import { Check } from 'lucide-react'

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
  error?: string
  helperText?: string
}

const Checkbox = React.forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`
    
    return (
      <div className="space-y-1">
        <div className="flex items-start space-x-3">
          <div className="relative flex items-center">
            <input
              id={checkboxId}
              type="checkbox"
              className={cn(
                'peer h-4 w-4 rounded border border-gray-600 bg-gray-900 text-emerald-500 focus:ring-2 focus:ring-emerald-300 focus:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50',
                error && 'border-red-500 focus:ring-2 focus:ring-red-300',
                className
              )}
              ref={ref}
              aria-invalid={error ? 'true' : 'false'}
              aria-describedby={error ? `${checkboxId}-error` : helperText ? `${checkboxId}-helper` : undefined}
              {...props}
            />
            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
              <Check className="h-3 w-3 text-white opacity-0 transition-opacity peer-checked:opacity-100" />
            </div>
          </div>
          {label && (
            <label htmlFor={checkboxId} className="text-sm font-medium text-gray-300 cursor-pointer">
              {label}
            </label>
          )}
        </div>
        {error && (
          <p id={`${checkboxId}-error`} className="text-sm text-red-400" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={`${checkboxId}-helper`} className="text-sm text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Checkbox.displayName = 'Checkbox'

export { Checkbox }
