import { ChangeEvent, useState } from 'react'

interface PasswordInputProps {
  id: string
  name: string
  value: string
  placeholder: string
  autoComplete: string
  onChange: (event: ChangeEvent<HTMLInputElement>) => void
}

function PasswordInput({
  id,
  name,
  value,
  placeholder,
  autoComplete,
  onChange,
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className="password-input">
      <input
        id={id}
        name={name}
        type={showPassword ? 'text' : 'password'}
        autoComplete={autoComplete}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
      />
      <button
        type="button"
        className="password-toggle"
        aria-label={showPassword ? 'Hide password' : 'Show password'}
        onClick={() => setShowPassword((visible) => !visible)}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          {showPassword ? (
            <>
              <path d="m3 3 18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.2A10.8 10.8 0 0 1 12 5c5.2 0 8.7 3.5 10 7-0.4 1.1-1.2 2.4-2.3 3.5M6.2 6.2C4.1 7.5 2.6 9.5 2 12c1.3 3.5 4.8 7 10 7 1.3 0 2.5-.2 3.6-.7" />
            </>
          ) : (
            <>
              <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
              <circle cx="12" cy="12" r="2.5" />
            </>
          )}
        </svg>
      </button>
    </div>
  )
}

export default PasswordInput
