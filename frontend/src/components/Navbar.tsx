import React from 'react'
import paperPicksLogo from '../assets/PaperPicksLogo.png'
import { useAuth } from '../context/useAuth'

interface NavbarProps {
  onNavigate?: (path: string) => void
}

function getInitials(username?: string): string {
  if (!username) return 'PP'
  const clean = username.trim()
  if (clean.length <= 2) return clean.toUpperCase()
  return clean.slice(0, 2).toUpperCase()
}

function Navbar({ onNavigate }: NavbarProps) {
  const { user, logout } = useAuth()

  async function handleLogout() {
    await logout()
    if (onNavigate) {
      onNavigate('/')
    } 
    else {
      window.location.assign('/')
    }
  }

  function handleNav(event: React.MouseEvent<HTMLAnchorElement>, path: string) {
    if (onNavigate) {
      event.preventDefault()
      onNavigate(path)
    }
  }

  return (
    <nav className="navbar" aria-label="Main navigation">
      <a className="navbar-brand" href="/props" onClick={(e) => handleNav(e, '/props')}>
        <img src={paperPicksLogo} alt="" />
        <span>PaperPicks</span>
      </a>

      <div className="navbar-links">
        <a className="navbar-link active" href="/props" aria-current="page">
          Games/Props
        </a>
        <a className="navbar-link" href="#my-bets">
          My Bets
        </a>
      </div>

      <div className="navbar-account">
        <a className="navbar-link" href="#leaderboard">
          Leaderboard
        </a>
        <span className="balance-pill" title="Virtual Currency Balance">
          {user ? user.balance.toLocaleString() : '10,000'}
        </span>
        {user ? (
          <div className="navbar-user-group">
            <button
              className="profile-button"
              type="button"
              aria-label={`Profile: ${user.username}`}
              title={`${user.username} (${user.role})`}
            >
              {getInitials(user.username)}
            </button>
            <button
              className="navbar-logout-button"
              type="button"
              onClick={handleLogout}
              title="Log out of PaperPicks"
            >
              Log out
            </button>
          </div>
        ) : (
          <a
            className="navbar-logout-button"
            href="/"
            onClick={(e) => handleNav(e, '/')}
          >
            Sign in
          </a>
        )}
      </div>
    </nav>
  )
}

export default Navbar
