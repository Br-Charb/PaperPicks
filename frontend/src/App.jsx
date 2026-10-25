import './App.css'
import paperPicksLogo from './assets/PaperPicksLogo.png'
import LoginForm from './components/LoginForm'

function BrandLogo() {
  return <img className="brand-logo" src={paperPicksLogo} alt="PaperPicks" />
}

function App() {
  return (
    <main className="login-page">
      <section className="login-intro" aria-label="PaperPicks introduction">
        <header className="brand">
          <BrandLogo />
          <span className="brand-name">PaperPicks</span>
        </header>

        <div className="intro-copy">
          <p className="eyebrow">Sports Betting</p>
          <h1>Practice your sports betting<br /><em>for free.</em></h1>
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
            <h2 id="login-heading">Login</h2>
          </div>

          <LoginForm />

          <p className="create-account">New to PaperPicks? <a href="#create-account" onClick={(event) => { event.preventDefault(); setMessage('Account creation is coming soon.') }}>Create an account</a></p>
        </div>
      </section>
    </main>
  )
}

export default App
