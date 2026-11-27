import { getAuthHeaders, parseErrorDetail } from './auth'
import { BalanceInfo, BalanceRestoreResult } from '../types'

export async function getBalance(): Promise<BalanceInfo> {
  const response = await fetch('/api/balance', {
    method: 'GET',
    headers: getAuthHeaders(),
    credentials: 'include',
  })

  const resJson = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  return resJson as BalanceInfo
}

export async function restoreBalance(): Promise<BalanceRestoreResult> {
  const response = await fetch('/api/balance/restore', {
    method: 'POST',
    headers: getAuthHeaders(),
    credentials: 'include',
  })

  const resJson = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  return resJson as BalanceRestoreResult
}

