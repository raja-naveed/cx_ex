import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { authApi } from '../lib/api'

export interface User {
  id: string
  email: string
  fullName: string
  username?: string
  emailVerified: boolean
  createdAt: string
}

export interface AuthContextType {
  user: User | null
  loading: boolean
  error: string | null
  login: (emailOrUsername: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (data: {
    fullName: string
    email: string
    password: string
    username?: string
    referralCode?: string
  }) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => setError(null)

  const login = async (emailOrUsername: string, password: string, rememberMe?: boolean) => {
    try {
      setLoading(true)
      setError(null)
      const response = await authApi.login({ emailOrUsername, password, rememberMe })
      setUser(response.user)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Login failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const register = async (data: {
    fullName: string
    email: string
    password: string
    username?: string
    referralCode?: string
  }) => {
    try {
      setLoading(true)
      setError(null)
      const response = await authApi.register(data)
      setUser(response.user)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
      setUser(null)
    } catch (err) {
      // Even if logout fails on server, clear local state
      setUser(null)
    }
  }

  const refresh = async () => {
    try {
      const response = await authApi.getMe()
      setUser(response.user)
    } catch (err) {
      setUser(null)
    }
  }

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setLoading(true)
        const response = await authApi.getMe()
        setUser(response.user)
      } catch (err) {
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refresh,
    clearError,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
