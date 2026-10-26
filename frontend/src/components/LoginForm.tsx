import { FormEvent, useState } from 'react'
import PasswordInput from './PasswordInput'
import { useAuth } from '../context/useAuth'

interface LoginFormProps {
  onCreateAccount: () => void
  onSuccess?: () => void
}

function LoginForm({ onCreateAccount, onSuccess }: LoginFormProps) {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!identifier.trim() || !password) {
      setMessage('Please enter your email or username and password.')
      return
    }

    setIsSubmitting(true)
    setMessage('')
    try {
      await login({ identifier: identifier.trim(), password })
      if (onSuccess) {
        onSuccess()
      } 
      else {
        window.history.pushState({}, '', '/props')
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    } 
    catch (err: any) {
      setMessage(err.message || 'Login failed. Please check your credentials.')
    } 
    finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="identifier">Email address or Username</label>
        <input
          id="identifier"
          name="identifier"
          type="text"
          autoComplete="username"
          placeholder="you@example.com or username"
          value={identifier}
          onChange={(event) => setIdentifier(event.target.value)}
          disabled={isSubmitting}
        />

        <div className="password-label">
          <label htmlFor="password">Password</label>
          <a
            href="#forgot-password"
            onClick={(event) => {
              event.preventDefault()
              setMessage('Password reset is not implemented yet.')
            }}
          >
            Forgot password?
          </a>
        </div>
        <PasswordInput
          id="password"
          name="password"
          autoComplete="current-password"
          placeholder="Enter your password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button className="submit-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in...' : 'Sign in'}{' '}
          <span aria-hidden="true">→</span>
        </button>
        <p className={`form-message${message ? ' form-message--visible' : ''}`} role="status">
          {message}
        </p>
      </form>

      <p className="create-account">
        New to PaperPicks?{' '}
        <a
          href="#create-account"
          onClick={(event) => {
            event.preventDefault()
            onCreateAccount()
          }}
        >
          Create an account
        </a>
      </p>
    </>
  )
}

export default LoginForm
