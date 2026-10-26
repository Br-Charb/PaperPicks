import { useEffect, useState } from 'react'
import './App.css'
import paperPicksLogo from './assets/PaperPicksLogo.png'
import LoginForm from './components/LoginForm'
import RegistrationForm from './components/RegistrationForm'
import { useAuth } from './context/useAuth'
import PropsDashboard from './pages/PropsDashboard'

function BrandLogo() {
  return <img className="brand-logo" src={paperPicksLogo} alt="" />
}

function AuthPage({
  isRegistration,
  onSwitchMode,
  onSuccess,
}: {
  isRegistration: boolean
  onSwitchMode: (mode: 'login' | 'register') => void
  onSuccess: () => void
}) {
  return (
    <main className="login-page">
      <section className="login-intro" aria-label="PaperPicks introduction">
        <header className="brand">
          <BrandLogo />
          <span className="brand-name">PaperPicks</span>
        </header>

        <div className="intro-copy">
          <p className="eyebrow">Sports Predictions</p>
          <h1>
            Practice your sports picks<br />
            <em>for free.</em>
          </h1>
          <p className="intro-description">
            Make free NFL predictions, test your instincts, and grow your virtual balance without risking real money.
          </p>
        </div>
      </section>

      <section className="login-panel" aria-labelledby="login-heading">
        <div className="login-card">
          <div className="mobile-brand brand">
            <BrandLogo />
            <span className="brand-name">PaperPicks</span>
          </div>
          <div className="login-heading">
            <h2 id="login-heading">{isRegistration ? 'Create your account' : 'Login'}</h2>
          </div>
          {isRegistration ? (
            <RegistrationForm
              onBackToLogin={() => onSwitchMode('login')}
              onSuccess={onSuccess}
            />
          ) : (
            <LoginForm
              onCreateAccount={() => onSwitchMode('register')}
              onSuccess={onSuccess}
            />
          )}
        </div>
      </section>
    </main>
  )
}

function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname)
  const { user, isLoading } = useAuth()

  useEffect(() => {
    function handleLocationChange() {
      setCurrentPath(window.location.pathname)
    }

    window.addEventListener('popstate', handleLocationChange)
    return () => window.removeEventListener('popstate', handleLocationChange)
  }, [])

  function navigate(path: string) {
    window.history.pushState({}, '', path)
    setCurrentPath(path)
  }

  if (isLoading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          background: '#07151e',
          color: '#ffffff',
          fontFamily: 'system-ui, sans-serif',
        }}
      >
        <p>Loading PaperPicks...</p>
      </div>
    )
  }

  // If authenticated and visiting root/register, show PropsDashboard
  if (currentPath === '/props' || (user && (currentPath === '/' || currentPath === '/register'))) {
    return <PropsDashboard onNavigate={navigate} />
  }

  return (
    <AuthPage
      isRegistration={currentPath === '/register'}
      onSwitchMode={(mode) => navigate(mode === 'register' ? '/register' : '/')}
      onSuccess={() => navigate('/props')}
    />
  )
}

export default App
