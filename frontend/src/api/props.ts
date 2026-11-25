import { getAuthHeaders, parseErrorDetail } from './auth'
import { DateGroup } from '../types'

export async function getAvailableProps(): Promise<DateGroup[]> {
  const response = await fetch('/api/props', {
    method: 'GET',
    headers: getAuthHeaders(),
    credentials: 'include',
  })

  const resJson = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  return resJson as DateGroup[]
}
