import { TokenResponse, User } from '../types'

const TOKEN_KEY = 'paperpicks_token'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } 
  else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }
  const token = getStoredToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

function parseErrorDetail(errorData: any): string {
  if (!errorData) {
    return 'Unknown error occurred.'
  }
  if (typeof errorData.detail === 'string') {
    return errorData.detail
  }
  if (Array.isArray(errorData.detail) && errorData.detail.length > 0) {
    return errorData.detail
      .map((item: any) => item.msg || item.message || JSON.stringify(item))
      .join('. ')
  }
  return errorData.message || 'Request failed. Please try again.'
}

export async function register(data: {
  username: string
  email: string
  password: string
}): Promise<TokenResponse> {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  })

  const resJson = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  const result = resJson as TokenResponse
  if (result.access_token) {
    setStoredToken(result.access_token)
  }
  return result
}

export async function login(data: {
  identifier: string
  password: string
}): Promise<TokenResponse> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      username_or_email: data.identifier,
      password: data.password,
    }),
  })

  const resJson = await response.json().catch(() => null)

  if (!response.ok) {
    throw new Error(parseErrorDetail(resJson))
  }

  const result = resJson as TokenResponse
  if (result.access_token) {
    setStoredToken(result.access_token)
  }
  return result
}

export async function logout(): Promise<void> {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      headers: getAuthHeaders(),
      credentials: 'include',
    })
  } 
  finally {
    setStoredToken(null)
  }
}

export async function getMe(): Promise<User | null> {
  try {
    const response = await fetch('/api/auth/me', {
      method: 'GET',
      headers: getAuthHeaders(),
      credentials: 'include',
    })

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        setStoredToken(null)
      }
      return null
    }

    return (await response.json()) as User
  } 
  catch {
    return null
  }
}
