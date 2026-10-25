import { FormEvent, useState } from 'react'
import PasswordInput from './PasswordInput'

interface RegistrationFormProps {
  onBackToLogin: () => void
}

function RegistrationForm({ onBackToLogin }: RegistrationFormProps) {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!email || !username || !password) {
      setMessage('Enter an email, username, and password to continue.')
      return
    }
    setMessage('This is a mockup — account creation is not connected yet.')
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
        />

        <label className="form-field-label" htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          autoComplete="username"
          placeholder="Choose a username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />

        <label className="form-field-label" htmlFor="registration-password">Password</label>
        <PasswordInput
          id="registration-password"
          name="password"
          autoComplete="new-password"
          placeholder="Create a password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />

        <button className="submit-button" type="submit">Create account <span aria-hidden="true">→</span></button>
        <p className={`form-message${message ? ' form-message--visible' : ''}`} role="status">{message}</p>
      </form>

      <p className="create-account">
        Already have an account?{' '}
        <a href="#login" onClick={(event) => { event.preventDefault(); onBackToLogin() }}>
          Log in
        </a>
      </p>
    </>
  )
}

export default RegistrationForm
