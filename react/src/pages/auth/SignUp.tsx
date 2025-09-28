import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthProvider'
import { signUpSchema, type SignUpFormData } from '../../lib/validation/authSchemas'
import { AuthLayout } from '../../layouts/AuthLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { PasswordInput } from '../../components/ui/PasswordInput'
import { Checkbox } from '../../components/ui/Checkbox'
import { Alert } from '../../components/ui/Alert'
import { PasswordStrengthBar } from '../../components/auth/PasswordStrengthBar'
import { Shield, Lock, User } from 'lucide-react'

const SignUp: React.FC = () => {
  const navigate = useNavigate()
  const { register: registerUser, loading, error, clearError } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPasswordStrength, setShowPasswordStrength] = useState(false)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isValid },
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: 'onChange',
  })

  const password = watch('password', '')

  const onSubmit = async (data: SignUpFormData) => {
    try {
      setIsSubmitting(true)
      clearError()
      await registerUser({
        fullName: data.fullName,
        email: data.email,
        password: data.password,
        username: data.username,
        referralCode: data.referralCode,
      })
      navigate('/app/dashboard')
    } catch (err) {
      // Error is handled by the auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Create your free account"
      subtitle="Learn, simulate, and build confidence"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Get started with ZEBRAT TRADING</h2>
          <p className="mt-2 text-sm text-gray-400">
            Already have an account?{' '}
            <Link
              to="/auth/login"
              className="font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              Sign in here
            </Link>
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" title="Registration failed">
            {error}
          </Alert>
        )}

        {/* Sign Up Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            {...register('fullName')}
            label="Full Name"
            placeholder="Enter your full name"
            error={errors.fullName?.message}
            autoComplete="name"
            autoFocus
          />

          <Input
            {...register('email')}
            type="email"
            label="Email Address"
            placeholder="Enter your email address"
            error={errors.email?.message}
            autoComplete="email"
          />

          <Input
            {...register('username')}
            label="Username (Optional)"
            placeholder="Choose a username"
            error={errors.username?.message}
            autoComplete="username"
            helperText="3-20 characters, lowercase letters, numbers, and underscores only"
          />

          <div className="space-y-2">
            <PasswordInput
              {...register('password')}
              label="Password"
              placeholder="Create a strong password"
              error={errors.password?.message}
              autoComplete="new-password"
              onFocus={() => setShowPasswordStrength(true)}
              onBlur={() => setShowPasswordStrength(false)}
            />
            {showPasswordStrength && password && (
              <PasswordStrengthBar password={password} />
            )}
          </div>

          <PasswordInput
            {...register('confirmPassword')}
            label="Confirm Password"
            placeholder="Confirm your password"
            error={errors.confirmPassword?.message}
            autoComplete="new-password"
          />

          <Input
            {...register('referralCode')}
            label="Referral Code (Optional)"
            placeholder="Enter referral code if you have one"
            error={errors.referralCode?.message}
          />

          <Checkbox
            {...register('agreeToTerms')}
            error={errors.agreeToTerms?.message}
            label={
              <span className="text-sm">
                I agree to the{' '}
                <Link to="/terms" className="text-primary-600 hover:text-primary-500">
                  Terms of Use
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
                  Privacy Policy
                </Link>
              </span>
            }
          />

          <Button
            type="submit"
            className="w-full"
            loading={isSubmitting}
            disabled={!isValid || isSubmitting}
          >
            {isSubmitting ? 'Creating account...' : 'Get started'}
          </Button>
        </form>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-base-200" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white text-base-500">Or continue with</span>
          </div>
        </div>

        {/* OAuth Button (Optional) */}
        <Button
          type="button"
          variant="secondary"
          className="w-full"
          disabled
        >
          Continue with Google
        </Button>

        {/* Security Notice */}
        <div className="mt-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
            <Shield className="w-4 h-4 mr-2 text-emerald-400" />
            Your data is secure
          </h3>
          <p className="text-xs text-gray-400">
            We use industry-standard encryption and never share your personal information. 
            This is an educational platform with no real money involved.
          </p>
        </div>
      </div>
    </AuthLayout>
  )
}

export default SignUp
