import { useState } from 'react'

function EyeIcon({ hidden }) {
  return hidden ? (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.2A10.8 10.8 0 0 1 12 5c5.2 0 8.7 3.5 10 7-0.4 1.1-1.2 2.4-2.3 3.5M6.2 6.2C4.1 7.5 2.6 9.5 2 12c1.3 3.5 4.8 7 10 7 1.3 0 2.5-.2 3.6-.7" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  )
}

function LoginForm() {
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    if (!email || !password) {
      setMessage('Enter your email and password to continue.')
      return
    }
    setMessage('This is a mockup — sign-in is not connected yet.')
  }

  return (
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
      <div className="password-input">
        <input
          id="password"
          name="password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="current-password"
          placeholder="Enter your password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button
          type="button"
          className="password-toggle"
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          onClick={() => setShowPassword((visible) => !visible)}
        >
          <EyeIcon hidden={showPassword} />
        </button>
      </div>
      <button className="submit-button" type="submit">Sign in <span aria-hidden="true">→</span></button>
      <p className={`form-message${message ? ' form-message--visible' : ''}`} role="status">{message}</p>
    </form>
  )
}

export default LoginForm
