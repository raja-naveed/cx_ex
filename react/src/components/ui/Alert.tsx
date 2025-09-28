import React from 'react'
import { cn } from '../../lib/utils'
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react'

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  children: React.ReactNode
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'info', title, children, ...props }, ref) => {
    const variants = {
      success: {
        container: 'bg-emerald-900/20 border-emerald-500/30 text-emerald-300',
        icon: 'text-emerald-400',
        Icon: CheckCircle,
      },
      error: {
        container: 'bg-red-900/20 border-red-500/30 text-red-300',
        icon: 'text-red-400',
        Icon: AlertCircle,
      },
      warning: {
        container: 'bg-yellow-900/20 border-yellow-500/30 text-yellow-300',
        icon: 'text-yellow-400',
        Icon: AlertTriangle,
      },
      info: {
        container: 'bg-gray-900/50 border-gray-700 text-gray-300',
        icon: 'text-gray-400',
        Icon: Info,
      },
    }

    const { container, icon, Icon } = variants[variant]

    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border p-4',
          container,
          className
        )}
        role="alert"
        {...props}
      >
        <div className="flex">
          <div className="flex-shrink-0">
            <Icon className={cn('h-5 w-5', icon)} aria-hidden="true" />
          </div>
          <div className="ml-3">
            {title && (
              <h3 className="text-sm font-medium mb-1">
                {title}
              </h3>
            )}
            <div className="text-sm">
              {children}
            </div>
          </div>
        </div>
      </div>
    )
  }
)

Alert.displayName = 'Alert'

export { Alert }
