import { useState } from 'react'
import { placeBet } from '../api/bets'
import { useAuth } from '../context/useAuth'
import { PickChoice, PlayerProp, SelectedPicks, ToastMessage } from '../types'
import PickToggle from './PickToggle'

interface PredictionSlipProps {
  props: PlayerProp[]
  selectedPicks: SelectedPicks
  onPick: (propId: string, choice: PickChoice) => void
  onRemove: (propId: string) => void
  onClear: () => void
  onNotify: (toast: Omit<ToastMessage, 'id'>) => void
}

const multipliers = [1, 1.5, 2, 2.6, 4, 6]
const wagerPresets = [50, 100, 250]

function deduplicateProps(items: PlayerProp[]): PlayerProp[] {
  const seen = new Set<string>()
  return items.filter((item) => {
    if (seen.has(item.id)) {
      return false
    }
    seen.add(item.id)
    return true
  })
}

function PredictionSlip({
  props,
  selectedPicks,
  onPick,
  onRemove,
  onClear,
  onNotify,
}: PredictionSlipProps) {
  const { user, updateBalance } = useAuth()
  const [wagerInput, setWagerInput] = useState('100')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const uniqueProps = deduplicateProps(props)
  const pickCount = uniqueProps.length
  const multiplier = multipliers[Math.min(pickCount, multipliers.length - 1)]

  const parsedWager = Number(wagerInput)
  const isWholePositive =
    wagerInput.trim() !== '' &&
    Number.isInteger(parsedWager) &&
    parsedWager > 0

  const availableBalance = user ? user.balance : 10000
  const exceedsBalance = isWholePositive && parsedWager > availableBalance
  const payout = isWholePositive ? Math.round(parsedWager * multiplier) : 0

  const canSubmit =
    Boolean(user) &&
    pickCount > 0 &&
    isWholePositive &&
    !exceedsBalance &&
    !isSubmitting

  function updateWager(nextValue: string) {
    const prevExceeds = isWholePositive && parsedWager > availableBalance
    setWagerInput(nextValue)

    const nextNum = Number(nextValue)
    const nextExceeds =
      nextValue.trim() !== '' &&
      Number.isInteger(nextNum) &&
      nextNum > availableBalance

    if (nextExceeds && !prevExceeds) {
      onNotify({
        type: 'warning',
        title: 'Insufficient Balance',
        message: `Wager of ${nextNum.toLocaleString()} PTS exceeds your available balance of ${availableBalance.toLocaleString()} PTS.`,
      })
    }
  }

  async function handleSubmit() {
    if (!user) {
      onNotify({
        type: 'error',
        title: 'Sign In Required',
        message: 'Please sign in before placing a prediction.',
      })
      return
    }

    if (!isWholePositive) {
      onNotify({
        type: 'warning',
        title: 'Invalid Wager',
        message: 'Enter a whole-number wager greater than 0.',
      })
      return
    }

    if (parsedWager > user.balance) {
      onNotify({
        type: 'warning',
        title: 'Insufficient Balance',
        message: `Wager of ${parsedWager.toLocaleString()} PTS exceeds your available balance of ${user.balance.toLocaleString()} PTS.`,
      })
      return
    }

    setIsSubmitting(true)
    try {
      const allNumericIds = uniqueProps.every((prop) =>
        /^\d+$/.test(prop.id),
      )

      if (allNumericIds) {
        const result = await placeBet({
          wager: parsedWager,
          legs: uniqueProps.map((prop) => ({
            prop_id: Number(prop.id),
            pick: selectedPicks[prop.id],
          })),
        })
        updateBalance(result.balance)
      } else {
        // Fallback for static demo props in data/props.ts
        updateBalance(user.balance - parsedWager)
      }

      onClear()
      onNotify({
        type: 'success',
        title: 'Prediction Placed!',
        message: `Locked in ${pickCount} ${pickCount === 1 ? 'pick' : 'picks'} for ${parsedWager.toLocaleString()} PTS (potential payout: ${payout.toLocaleString()} PTS).`,
      })
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Could not place prediction.'
      onNotify({
        type: 'error',
        title: 'Prediction Failed',
        message,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <aside className="prediction-slip" aria-labelledby="slip-heading">
      <div className="slip-heading">
        <h2 id="slip-heading">Prediction Slip</h2>
        <span>{pickCount} {pickCount === 1 ? 'Pick' : 'Picks'}</span>
      </div>

      <div className="slip-list">
        {pickCount === 0 ? (
          <div className="empty-slip">
            <p>Your slip is empty.</p>
            <span>Choose Over or Under on a prop to add a pick.</span>
          </div>
        ) : (
          uniqueProps.map((prop) => (
            <article className="slip-card" key={prop.id}>
              <button
                className="remove-pick"
                type="button"
                aria-label={`Remove ${prop.player}`}
                onClick={() => onRemove(prop.id)}
              >
                ×
              </button>
              <h3>{prop.player}</h3>
              <p>
                {prop.category === 'Game Outcome' ? 'To win by' : prop.category}: <strong>{prop.line}</strong>
              </p>
              <div className="slip-meta">
                <span>{prop.matchup}</span>
                <span>{prop.time}</span>
              </div>
              <PickToggle
                value={selectedPicks[prop.id]}
                label={`Change pick for ${prop.player}`}
                onChange={(choice) => onPick(prop.id, choice)}
              />
            </article>
          ))
        )}
      </div>

      <div className="slip-summary">
        <div className="slip-wager">
          <div className="slip-wager__header">
            <label htmlFor="slip-wager-input">Wager (PTS)</label>
            <span className="slip-wager__available">
              Available: {availableBalance.toLocaleString()} PTS
            </span>
          </div>

          <input
            id="slip-wager-input"
            type="number"
            min={1}
            step={1}
            inputMode="numeric"
            value={wagerInput}
            onChange={(event) => updateWager(event.target.value)}
            className={`slip-wager__input${exceedsBalance ? ' slip-wager__input--error' : ''}`}
            aria-invalid={exceedsBalance || !isWholePositive}
            placeholder="Enter wager"
          />

          <div className="wager-presets" role="group" aria-label="Quick wager amounts">
            {wagerPresets.map((preset) => (
              <button
                key={preset}
                type="button"
                className="wager-preset-btn"
                onClick={() => updateWager(String(preset))}
              >
                {preset}
              </button>
            ))}
            <button
              type="button"
              className="wager-preset-btn"
              disabled={availableBalance <= 0}
              onClick={() => updateWager(String(availableBalance))}
            >
              Max
            </button>
          </div>
        </div>

        {exceedsBalance && (
          <p className="slip-alert" role="alert">
            Wager exceeds your available balance of {availableBalance.toLocaleString()} PTS.
          </p>
        )}

        {!isWholePositive && wagerInput.trim() !== '' && (
          <p className="slip-alert" role="alert">
            Enter a whole-number wager greater than 0.
          </p>
        )}

        <div><span>Total picks</span><strong>{pickCount}</strong></div>
        <div><span>Potential multiplier</span><strong>{multiplier.toFixed(1)}x</strong></div>
        <div><span>Potential payout</span><strong>{payout.toLocaleString()} PTS</strong></div>

        <button type="button" disabled={!canSubmit} onClick={handleSubmit}>
          {isSubmitting ? 'Placing Prediction...' : 'Place Prediction'}
        </button>
      </div>
    </aside>
  )
}

export default PredictionSlip
