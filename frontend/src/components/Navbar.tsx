import paperPicksLogo from '../assets/PaperPicksLogo.png'

function Navbar() {
  return (
    <nav className="navbar" aria-label="Main navigation">
      <a className="navbar-brand" href="/props">
        <img src={paperPicksLogo} alt="" />
        <span>PaperPicks</span>
      </a>

      <div className="navbar-links">
        <a className="navbar-link active" href="/props" aria-current="page">Games/Props</a>
        <a className="navbar-link" href="#my-bets">My Bets</a>
      </div>

      <div className="navbar-account">
        <a className="navbar-link" href="#leaderboard">Leaderboard</a>
        <span className="balance-pill">10,000</span>
        <button className="profile-button" type="button" aria-label="Open profile">BC</button>
      </div>
    </nav>
  )
}

export default Navbar
