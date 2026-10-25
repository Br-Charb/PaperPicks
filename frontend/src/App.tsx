import { useState } from 'react'
import './App.css'
import paperPicksLogo from './assets/PaperPicksLogo.png'
import LoginForm from './components/LoginForm'
import RegistrationForm from './components/RegistrationForm'
import PropsDashboard from './pages/PropsDashboard'

function BrandLogo() {
  return <img className="brand-logo" src={paperPicksLogo} alt="" />
}

function AuthPage() {
  const [isRegistration, setIsRegistration] = useState(window.location.pathname === '/register')

  function showRegistration() {
    window.history.pushState({}, '', '/register')
    setIsRegistration(true)
  }

  function showLogin() {
    window.history.pushState({}, '', '/')
    setIsRegistration(false)
  }

  return (
    <main className="login-page">
      <section className="login-intro" aria-label="PaperPicks introduction">
        <header className="brand">
          <BrandLogo />
          <span className="brand-name">PaperPicks</span>
        </header>

        <div className="intro-copy">
          <p className="eyebrow">Sports Predictions</p>
          <h1>Practice your sports picks<br /><em>for free.</em></h1>
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
            <RegistrationForm onBackToLogin={showLogin} />
          ) : (
            <LoginForm onCreateAccount={showRegistration} />
          )}
        </div>
      </section>
    </main>
  )
}

function App() {
  return window.location.pathname === '/props' ? <PropsDashboard /> : <AuthPage />
}

export default App
