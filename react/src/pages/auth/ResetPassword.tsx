import React, { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { resetPasswordSchema, type ResetPasswordFormData } from '../../lib/validation/authSchemas'
import { authApi } from '../../lib/api'
import { AuthLayout } from '../../layouts/AuthLayout'
import { Button } from '../../components/ui/Button'
import { PasswordInput } from '../../components/ui/PasswordInput'
import { Alert } from '../../components/ui/Alert'
import { PasswordStrengthBar } from '../../components/auth/PasswordStrengthBar'
import { CheckCircle, ArrowLeft } from 'lucide-react'

const ResetPassword: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPasswordStrength, setShowPasswordStrength] = useState(false)

  const token = searchParams.get('token')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    mode: 'onChange',
  })

  const password = watch('newPassword', '')

  useEffect(() => {
    if (!token) {
      setError('Invalid or missing reset token')
    }
  }, [token])

  const onSubmit = async (data: ResetPasswordFormData) => {
    if (!token) return

    try {
      setIsSubmitting(true)
      setError(null)
      await authApi.resetPassword(token, data.newPassword)
      setIsSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to reset password')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSuccess) {
    return (
      <AuthLayout
        title="Password reset successful"
        subtitle="Your password has been updated successfully"
      >
        <div className="space-y-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold text-white">Password reset successful</h2>
            <p className="mt-2 text-sm text-gray-400">
              Your password has been updated. You can now sign in with your new password.
            </p>
          </div>

          <Alert variant="success">
            <p className="text-sm">
              Your password has been successfully updated. You can now sign in to your account.
            </p>
          </Alert>

          <div className="space-y-3">
            <Button
              onClick={() => navigate('/auth/login')}
              className="w-full"
            >
              Continue to sign in
            </Button>
            
            <div className="text-center">
              <Link
                to="/"
                className="inline-flex items-center text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to home
              </Link>
            </div>
          </div>
        </div>
      </AuthLayout>
    )
  }

  if (!token) {
    return (
      <AuthLayout
        title="Invalid reset link"
        subtitle="This password reset link is invalid or has expired"
      >
        <div className="space-y-6">
          <Alert variant="error" title="Invalid reset link">
            This password reset link is invalid or has expired. Please request a new one.
          </Alert>

          <div className="text-center">
            <Link
              to="/auth/forgot-password"
              className="inline-flex items-center text-sm text-primary-600 hover:text-primary-500 transition-colors"
            >
              Request new reset link
            </Link>
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Set new password"
      subtitle="Choose a strong password for your account"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Set your new password</h2>
          <p className="mt-2 text-sm text-gray-400">
            Choose a strong password to secure your account.
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
          <div className="space-y-2">
            <PasswordInput
              {...register('newPassword')}
              label="New Password"
              placeholder="Enter your new password"
              error={errors.newPassword?.message}
              autoComplete="new-password"
              autoFocus
              onFocus={() => setShowPasswordStrength(true)}
              onBlur={() => setShowPasswordStrength(false)}
            />
            {showPasswordStrength && password && (
              <PasswordStrengthBar password={password} />
            )}
          </div>

          <PasswordInput
            {...register('confirmPassword')}
            label="Confirm New Password"
            placeholder="Confirm your new password"
            error={errors.confirmPassword?.message}
            autoComplete="new-password"
          />

          <Button
            type="submit"
            className="w-full"
            loading={isSubmitting}
            disabled={!isValid || isSubmitting}
          >
            {isSubmitting ? 'Updating password...' : 'Update password'}
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

export default ResetPassword
