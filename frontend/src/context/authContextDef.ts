import { createContext } from 'react'
import { BalanceRestoreResult, User } from '../types'

export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: { identifier: string; password: string }) => Promise<void>
  register: (data: { username: string; email: string; password: string }) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  updateBalance: (newBalance: number) => void
  restoreBalance: () => Promise<BalanceRestoreResult>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

