import React, { useState } from 'react'
import paperPicksLogo from '../assets/PaperPicksLogo.png'
import { useAuth } from '../context/useAuth'
import BalanceModal from './BalanceModal'

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
  const [isBalanceModalOpen, setIsBalanceModalOpen] = useState(false)

  async function handleLogout() {
    await logout()
    if (onNavigate) {
      onNavigate('/')
    } else {
      window.location.assign('/')
    }
  }

  function handleNav(event: React.MouseEvent<HTMLAnchorElement>, path: string) {
    if (onNavigate) {
      event.preventDefault()
      onNavigate(path)
    }
  }

  const currentBalance = user ? user.balance : 10000
  const isZeroBalance = user ? user.balance === 0 : false

  return (
    <>
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

          {user ? (
            <button
              type="button"
              className={`balance-pill balance-pill--interactive${
                isZeroBalance ? ' balance-pill--zero' : ''
              }`}
              onClick={() => setIsBalanceModalOpen(true)}
              title="Click to view virtual balance details or claim reload"
              aria-label={`Virtual currency balance: ${currentBalance.toLocaleString()} points. Click to manage.`}
            >
              <span className="balance-pill__icon" aria-hidden="true">🪙</span>
              <span className="balance-pill__amount">{currentBalance.toLocaleString()}</span>
              {isZeroBalance && (
                <span className="balance-pill__badge" aria-label="Reload available">
                  Reload
                </span>
              )}
            </button>
          ) : (
            <span className="balance-pill" title="Virtual Currency Balance">
              10,000
            </span>
          )}

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

      <BalanceModal
        isOpen={isBalanceModalOpen}
        onClose={() => setIsBalanceModalOpen(false)}
      />
    </>
  )
}

export default Navbar
