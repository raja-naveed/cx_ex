import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link } from 'react-router-dom'
import { forgotPasswordSchema, type ForgotPasswordFormData } from '../../lib/validation/authSchemas'
import { authApi } from '../../lib/api'
import { AuthLayout } from '../../layouts/AuthLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Alert } from '../../components/ui/Alert'
import { ArrowLeft, Mail } from 'lucide-react'

const ForgotPassword: React.FC = () => {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    mode: 'onChange',
  })

  const onSubmit = async (data: ForgotPasswordFormData) => {
    try {
      setIsSubmitting(true)
      setError(null)
      await authApi.requestPasswordReset(data.email)
      setIsSubmitted(true)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to send reset email')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <AuthLayout
        title="Check your email"
        subtitle="We've sent you a password reset link"
      >
        <div className="space-y-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Check your email</h2>
            <p className="mt-2 text-sm text-gray-400">
              We've sent a password reset link to your email address. 
              Please check your inbox and follow the instructions.
            </p>
          </div>

          <Alert variant="info">
            <p className="text-sm">
              <strong>Didn't receive the email?</strong> Check your spam folder or{' '}
              <button
                onClick={() => setIsSubmitted(false)}
                className="text-primary-600 hover:text-primary-500 underline"
              >
                try again
              </button>
            </p>
          </Alert>

          <div className="text-center">
            <Link
              to="/auth/login"
              className="inline-flex items-center text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to sign in
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Reset your password"
      subtitle="Enter your email address and we'll send you a reset link"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Forgot your password?</h2>
          <p className="mt-2 text-sm text-gray-400">
            No worries! Enter your email address and we'll send you a reset link.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" title="Reset failed">
            {error}
          </Alert>
        )}

        {/* Reset Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            {...register('email')}
            type="email"
            label="Email Address"
            placeholder="Enter your email address"
            error={errors.email?.message}
            autoComplete="email"
            autoFocus
          />

          <Button
            type="submit"
            className="w-full"
            loading={isSubmitting}
            disabled={!isValid || isSubmitting}
          >
            {isSubmitting ? 'Sending reset link...' : 'Send reset link'}
          </Button>
        </form>

        {/* Back to Login */}
        <div className="text-center">
          <Link
            to="/auth/login"
            className="inline-flex items-center text-sm text-primary-600 hover:text-primary-500 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to sign in
          </Link>
        </div>
      </div>
    </AuthLayout>
  )
}

export default ForgotPassword
