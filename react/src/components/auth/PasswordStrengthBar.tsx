import React from 'react'
import { cn } from '../../lib/utils'
import { Check, X } from 'lucide-react'

export interface PasswordStrengthBarProps {
  password: string
  className?: string
}

interface PasswordCriteria {
  label: string
  test: (password: string) => boolean
}

const criteria: PasswordCriteria[] = [
  {
    label: 'At least 10 characters',
    test: (password) => password.length >= 10,
  },
  {
    label: 'One uppercase letter',
    test: (password) => /[A-Z]/.test(password),
  },
  {
    label: 'One lowercase letter',
    test: (password) => /[a-z]/.test(password),
  },
  {
    label: 'One number',
    test: (password) => /[0-9]/.test(password),
  },
  {
    label: 'One special character',
    test: (password) => /[^A-Za-z0-9]/.test(password),
  },
]

const getStrengthLevel = (password: string): number => {
  return criteria.filter(criterion => criterion.test(password)).length
}

const getStrengthColor = (strength: number): string => {
  if (strength === 0) return 'bg-gray-700'
  if (strength <= 2) return 'bg-red-500'
  if (strength <= 3) return 'bg-yellow-500'
  if (strength <= 4) return 'bg-emerald-500'
  return 'bg-emerald-600'
}

const getStrengthLabel = (strength: number): string => {
  if (strength === 0) return 'Enter a password'
  if (strength <= 2) return 'Weak'
  if (strength <= 3) return 'Fair'
  if (strength <= 4) return 'Good'
  return 'Strong'
}

const PasswordStrengthBar: React.FC<PasswordStrengthBarProps> = ({ password, className }) => {
  const strength = getStrengthLevel(password)
  const strengthColor = getStrengthColor(strength)
  const strengthLabel = getStrengthLabel(strength)
  const strengthPercentage = (strength / criteria.length) * 100

  return (
    <div className={cn('space-y-3', className)}>
      {/* Strength Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Password strength</span>
          <span className={cn(
            'font-medium',
            strength === 0 && 'text-gray-500',
            strength <= 2 && 'text-red-400',
            strength <= 3 && 'text-yellow-400',
            strength <= 4 && 'text-emerald-400',
            strength === 5 && 'text-emerald-300'
          )}>
            {strengthLabel}
          </span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-300 ease-out',
              strengthColor
            )}
            style={{ width: `${strengthPercentage}%` }}
          />
        </div>
      </div>

      {/* Criteria Checklist */}
      <div className="space-y-2">
        {criteria.map((criterion, index) => {
          const isValid = criterion.test(password)
          return (
            <div key={index} className="flex items-center space-x-2 text-sm">
              <div className="flex-shrink-0">
                {isValid ? (
                  <Check className="h-4 w-4 text-emerald-400" />
                ) : (
                  <X className="h-4 w-4 text-gray-500" />
                )}
              </div>
              <span className={cn(
                'transition-colors',
                isValid ? 'text-emerald-400' : 'text-gray-400'
              )}>
                {criterion.label}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export { PasswordStrengthBar }
