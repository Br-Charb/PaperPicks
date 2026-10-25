import { FormEvent, useState } from 'react'
import PasswordInput from './PasswordInput'

interface LoginFormProps {
  onCreateAccount: () => void
}

function LoginForm({ onCreateAccount }: LoginFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    window.location.assign('/props')
  }

  return (
    <>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="email">Email address</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <div className="password-label">
          <label htmlFor="password">Password</label>
          <a href="#forgot-password" onClick={(event) => { event.preventDefault(); setMessage('Password reset is coming soon.') }}>
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
        <button className="submit-button" type="submit">Sign in <span aria-hidden="true">→</span></button>
        <p className={`form-message${message ? ' form-message--visible' : ''}`} role="status">{message}</p>
      </form>

      <p className="create-account">
        New to PaperPicks?{' '}
        <a href="#create-account" onClick={(event) => { event.preventDefault(); onCreateAccount() }}>
          Create an account
        </a>
      </p>
    </>
  )
}

export default LoginForm
