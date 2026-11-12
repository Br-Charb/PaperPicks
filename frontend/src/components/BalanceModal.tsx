import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '../context/useAuth'

interface BalanceModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function BalanceModal({ isOpen, onClose }: BalanceModalProps) {
  const { user, restoreBalance } = useAuth()
  const [isRestoring, setIsRestoring] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const handleClose = useCallback(() => {
    setFeedback(null)
    onClose()
  }, [onClose])

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape' && isOpen) {
        handleClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, handleClose])

  if (!isOpen || !user) {
    return null
  }

  const currentBalance = user.balance
  const canRestore = currentBalance === 0

  async function handleClaimReload() {
    setIsRestoring(true)
    setFeedback(null)
    try {
      const result = await restoreBalance()
      setFeedback({
        type: 'success',
        message: result.message || '1,000 units added to your virtual balance!',
      })
    } catch (err: any) {
      setFeedback({
        type: 'error',
        message: err.message || 'Could not restore balance. Please try again.',
      })
    } finally {
      setIsRestoring(false)
    }
  }

  return (
    <div
      className="balance-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="balance-modal-title"
      onClick={handleClose}
    >
      <div
        className="balance-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="balance-modal__header">
          <div>
            <span className="balance-modal__eyebrow">Virtual Currency</span>
            <h2 id="balance-modal-title">PaperPicks Wallet</h2>
          </div>
          <button
            type="button"
            className="balance-modal__close-button"
            aria-label="Close balance window"
            onClick={handleClose}
          >
            ×
          </button>
        </header>

        <section className="balance-modal__summary-card">
          <div className="balance-modal__amount-group">
            <span className="balance-modal__coin-icon" aria-hidden="true">🪙</span>
            <div>
              <span className="balance-modal__amount-label">Current Balance</span>
              <div className="balance-modal__amount-value">
                {currentBalance.toLocaleString()}
                <span className="balance-modal__currency-unit">PTS</span>
              </div>
            </div>
          </div>
          <div className="balance-modal__status-tag">
            {canRestore ? 'Reload Ready' : 'Active Funds'}
          </div>
        </section>

        {feedback && (
          <div
            className={`balance-modal__feedback balance-modal__feedback--${feedback.type}`}
            role="status"
          >
            {feedback.message}
          </div>
        )}

        <section className="balance-modal__section">
          <h3>Balance Restoration</h3>
          <p className="balance-modal__description">
            PaperPicks uses free virtual currency. When your balance reaches <strong>0 PTS</strong>,
            you can instantly claim a <strong>1,000 PTS reload</strong> to continue making NFL predictions.
          </p>

          <div className="balance-modal__action-row">
            <button
              type="button"
              className="balance-modal__claim-button"
              disabled={!canRestore || isRestoring}
              onClick={handleClaimReload}
            >
              {isRestoring ? 'Claiming Reload...' : 'Claim 1,000 PTS Reload'}
            </button>
          </div>
          {!canRestore && (
            <span className="balance-modal__subtext">
              Reload is unlocked when your balance reaches 0 PTS.
            </span>
          )}
        </section>

        <section className="balance-modal__section balance-modal__history">
          <div className="balance-modal__section-header">
            <h3>Recent Balance Activity</h3>
            <span className="balance-modal__mock-badge">Live Mockup</span>
          </div>
          <ul className="balance-modal__activity-list">
            <li className="balance-modal__activity-item">
              <div className="balance-modal__activity-info">
                <strong>Welcome Bonus</strong>
                <span>Initial account balance grant</span>
              </div>
              <span className="balance-modal__activity-credit">+10,000 PTS</span>
            </li>
            {currentBalance > 0 && currentBalance < 10000 && (
              <li className="balance-modal__activity-item">
                <div className="balance-modal__activity-info">
                  <strong>Prediction Slips Placed</strong>
                  <span>Wager deductions</span>
                </div>
                <span className="balance-modal__activity-debit">
                  -{(10000 - currentBalance).toLocaleString()} PTS
                </span>
              </li>
            )}
            {canRestore && (
              <li className="balance-modal__activity-item balance-modal__activity-item--zero">
                <div className="balance-modal__activity-info">
                  <strong>Zero Balance Reached</strong>
                  <span>Eligible for 1,000 reload</span>
                </div>
                <span className="balance-modal__activity-zero">0 PTS</span>
              </li>
            )}
          </ul>
        </section>
      </div>
    </div>
  )
}
