import './App.css'
import LoginForm from './components/LoginForm'

function BrandMark() {
  return (
    <div className="brand-mark" aria-hidden="true">
      <span className="brand-mark__page brand-mark__page--back" />
      <span className="brand-mark__page brand-mark__page--middle" />
      <span className="brand-mark__page brand-mark__page--front">
        <span />
        <span />
        <span />
      </span>
    </div>
  )
}

function App() {
  return (
    <main className="login-page">
      <section className="login-intro" aria-label="PaperPicks introduction">
        <header className="brand">
          <BrandMark />
          <span>PaperPicks</span>
        </header>

        <div className="intro-copy">
          <p className="eyebrow">Sports Betting</p>
          <h1>Practice your sports betting<br /><em>for free.</em></h1>
          <p className="intro-description">
            lorem ipsum dolor sit amet consectetur adipiscing elit consequat est eos est dolores optio nihil cillum cupiditate
          </p>
        </div>
      </section>

      <section className="login-panel" aria-labelledby="login-heading">
        <div className="login-card">
          <div className="mobile-brand brand">
            <BrandMark />
            <span>PaperPicks</span>
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
