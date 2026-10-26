import { FormEvent, useState } from 'react'
import PasswordInput from './PasswordInput'
import { useAuth } from '../context/useAuth'

interface RegistrationFormProps {
  onBackToLogin: () => void
  onSuccess?: () => void
}

function RegistrationForm({ onBackToLogin, onSuccess }: RegistrationFormProps) {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { register } = useAuth()

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const cleanEmail = email.trim()
    const cleanUsername = username.trim()

    if (!cleanEmail || !cleanUsername || !password) {
      setMessage('Enter an email, username, and password to continue.')
      return
    }

    if (cleanUsername.length < 3) {
      setMessage('Username must be at least 3 characters long.')
      return
    }

    if (password.length < 6) {
      setMessage('Password must be at least 6 characters long.')
      return
    }

    setIsSubmitting(true)
    setMessage('')
    try {
      await register({
        email: cleanEmail,
        username: cleanUsername,
        password,
      })
      if (onSuccess) {
        onSuccess()
      } 
      else {
        window.history.pushState({}, '', '/props')
        window.dispatchEvent(new PopStateEvent('popstate'))
      }
    } 
    catch (err: any) {
      setMessage(err.message || 'Registration failed. Please check your details.')
    } 
    finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="registration-email">Email address</label>
        <input
          id="registration-email"
          name="email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          disabled={isSubmitting}
        />

        <label className="form-field-label" htmlFor="username">
          Username
        </label>
        <input
          id="username"
          name="username"
          type="text"
          autoComplete="username"
          placeholder="Choose a username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          disabled={isSubmitting}
        />

        <label className="form-field-label" htmlFor="registration-password">
          Password
        </label>
        <PasswordInput
          id="registration-password"
          name="password"
          autoComplete="new-password"
          placeholder="Create a password (min 6 characters)"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button className="submit-button" type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account...' : 'Create account'}{' '}
          <span aria-hidden="true">→</span>
        </button>
        <p className={`form-message${message ? ' form-message--visible' : ''}`} role="status">
          {message}
        </p>
      </form>

      <p className="create-account">
        Already have an account?{' '}
        <a
          href="#login"
          onClick={(event) => {
            event.preventDefault()
            onBackToLogin()
          }}
        >
          Log in
        </a>
      </p>
    </>
  )
}

export default RegistrationForm
