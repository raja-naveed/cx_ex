import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthProvider'
import { loginSchema, type LoginFormData } from '../../lib/validation/authSchemas'
import { AuthLayout } from '../../layouts/AuthLayout'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { Checkbox } from '../../components/ui/Checkbox'
import { Alert } from '../../components/ui/Alert'
import { Spinner } from '../../components/ui/Spinner'
import { ArrowRight, Shield, Zap } from 'lucide-react'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const { login, loading, error, clearError } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onChange',
  })

  const onSubmit = async (data: LoginFormData) => {
    try {
      setIsSubmitting(true)
      clearError()
      await login(data.emailOrUsername, data.password, data.rememberMe)
      navigate('/app/dashboard')
    } catch (err) {
      // Error is handled by the auth context
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Practice trading in a risk‑free environment"
    >
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white">Sign in to your account</h2>
          <p className="mt-2 text-sm text-gray-400">
            Don't have an account?{' '}
            <Link
              to="/auth/signup"
              className="font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              Create one here
            </Link>
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="error" title="Sign in failed">
            {error}
          </Alert>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            {...register('emailOrUsername')}
            label="Email or Username"
            placeholder="Enter your email or username"
            error={errors.emailOrUsername?.message}
            autoComplete="username"
            autoFocus
          />

          <Input
            {...register('password')}
            type="password"
            label="Password"
            placeholder="Enter your password"
            error={errors.password?.message}
            autoComplete="current-password"
          />

          <div className="flex items-center justify-between">
            <Checkbox
              {...register('rememberMe')}
              label="Remember me"
            />
            <Link
              to="/auth/forgot-password"
              className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              Forgot password?
            </Link>
          </div>

          <Button
            type="submit"
            className="w-full"
            loading={isSubmitting}
            disabled={!isValid || isSubmitting}
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
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

        {/* Demo Account Info */}
        <div className="mt-6 p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
            <Zap className="w-4 h-4 mr-2 text-emerald-400" />
            Demo Account
          </h3>
          <p className="text-xs text-gray-400 mb-2">
            Try the platform with a demo account:
          </p>
          <div className="text-xs text-gray-500 space-y-1">
            <div>Email: demo@example.com</div>
            <div>Password: demo123</div>
          </div>
        </div>
      </div>
    </AuthLayout>
  )
}

export default Login
