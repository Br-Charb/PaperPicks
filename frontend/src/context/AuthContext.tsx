import React, { useEffect, useState } from 'react'
import * as authApi from '../api/auth'
import { User } from '../types'
import { AuthContext } from './authContextDef'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  async function refreshUser() {
    try {
      const currentUser = await authApi.getMe()
      setUser(currentUser)
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    let active = true

    async function initAuth() {
      try {
        const currentUser = await authApi.getMe()
        if (active) {
          setUser(currentUser)
        }
      } catch {
        if (active) {
          setUser(null)
        }
      } finally {
        if (active) {
          setIsLoading(false)
        }
      }
    }

    void initAuth()

    return () => {
      active = false
    }
  }, [])

  async function login(data: { identifier: string; password: string }) {
    const res = await authApi.login(data)
    setUser(res.user)
  }

  async function register(data: { username: string; email: string; password: string }) {
    const res = await authApi.register(data)
    setUser(res.user)
  }

  async function logout() {
    await authApi.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
