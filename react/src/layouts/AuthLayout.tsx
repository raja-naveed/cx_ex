import React from 'react'
import { cn } from '../lib/utils'
import { TrendingUp, Shield, Zap, BarChart3 } from 'lucide-react'

interface AuthLayoutProps {
  children: React.ReactNode
  title: string
  subtitle: string
  className?: string
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ 
  children, 
  title, 
  subtitle, 
  className 
}) => {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left side - Marketing content */}
        <div className="hidden lg:block space-y-8">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-brand-gradient rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">Z</span>
              </div>
              <span className="text-2xl font-bold text-white">ZEBRAT TRADING</span>
            </div>
            <h1 className="text-4xl font-bold text-white leading-tight">
              {title}
            </h1>
            <p className="text-lg text-gray-300">
              {subtitle}
            </p>
          </div>
          
          {/* Features list */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
                <TrendingUp className="w-3 h-3 text-emerald-400" />
              </div>
              <span className="text-gray-300">Practice trading with virtual money</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
                <BarChart3 className="w-3 h-3 text-emerald-400" />
              </div>
              <span className="text-gray-300">Real-time market simulation</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-emerald-500/20 rounded-full flex items-center justify-center">
                <Shield className="w-3 h-3 text-emerald-400" />
              </div>
              <span className="text-gray-300">Learn without financial risk</span>
            </div>
          </div>

          {/* Abstract illustration */}
          <div className="relative">
            <div className="absolute inset-0 bg-brand-gradient opacity-10 rounded-3xl transform rotate-3"></div>
            <div className="relative bg-gray-900 rounded-2xl p-8 shadow-lg border border-gray-800">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="w-16 h-16 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                    <TrendingUp className="w-8 h-8 text-emerald-400" />
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">$12,345.67</div>
                    <div className="text-sm text-emerald-400">+$234.56 (1.96%)</div>
                  </div>
                </div>
                <div className="h-20 bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-lg flex items-center justify-center">
                  <div className="text-black text-sm font-medium">Portfolio Performance</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Auth form */}
        <div className="w-full max-w-md mx-auto">
          <div className={cn(
            'bg-gray-900 rounded-xl shadow-lg p-6 md:p-8 border border-gray-800',
            className
          )}>
            {children}
          </div>
          
          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-400">
              ZEBRAT TRADING is an educational simulator. No real money or live brokerage access.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export { AuthLayout }
