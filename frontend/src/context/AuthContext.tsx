import React, { useEffect, useState } from 'react'
import * as authApi from '../api/auth'
import * as balanceApi from '../api/balance'
import { BalanceRestoreResult, User } from '../types'
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

  // Keep currency balance synced in real time when the user returns to the tab
  useEffect(() => {
    const userId = user?.id
    if (!userId) {
      return
    }

    let active = true

    async function syncBalance() {
      try {
        const info = await balanceApi.getBalance()
        if (active) {
          setUser((prev) => (prev ? { ...prev, balance: info.balance } : null))
        }
      } catch {
        // Ignore transient sync errors on focus
      }
    }

    window.addEventListener('focus', syncBalance)
    const interval = window.setInterval(syncBalance, 30000)

    return () => {
      active = false
      window.removeEventListener('focus', syncBalance)
      window.clearInterval(interval)
    }
  }, [user?.id])

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

  function updateBalance(newBalance: number) {
    setUser((prev) => (prev ? { ...prev, balance: newBalance } : null))
  }

  async function restoreBalance(): Promise<BalanceRestoreResult> {
    const result = await balanceApi.restoreBalance()
    updateBalance(result.balance)
    return result
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
        updateBalance,
        restoreBalance,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
