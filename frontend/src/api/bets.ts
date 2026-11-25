import { getAuthHeaders, parseErrorDetail } from './auth'
import { BetCreatePayload, BetPlacementResult, BetRecord } from '../types'

export async function placeBet(payload: BetCreatePayload): Promise<BetPlacementResult> {
  const response = await fetch('/api/bets', {
    method: 'POST',
    headers: getAuthHeaders(),
    credentials: 'include',
    body: JSON.stringify(payload),
  })

  const resJson = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  return resJson as BetPlacementResult
}

export async function getMyBets(): Promise<BetRecord[]> {
  const response = await fetch('/api/bets', {
    method: 'GET',
    headers: getAuthHeaders(),
    credentials: 'include',
  })

  const resJson = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  return resJson as BetRecord[]
}
