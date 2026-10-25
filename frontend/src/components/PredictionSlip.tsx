import { PickChoice, PlayerProp, SelectedPicks } from '../types'
import PickToggle from './PickToggle'

interface PredictionSlipProps {
  props: PlayerProp[]
  selectedPicks: SelectedPicks
  onPick: (propId: string, choice: PickChoice) => void
  onRemove: (propId: string) => void
}

const multipliers = [1, 1.5, 2, 2.6, 4, 6]

function PredictionSlip({ props, selectedPicks, onPick, onRemove }: PredictionSlipProps) {
  const pickCount = props.length
  const multiplier = multipliers[Math.min(pickCount, multipliers.length - 1)]
  const payout = Math.round(10000 * multiplier).toLocaleString()

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
          props.map((prop) => (
            <article className="slip-card" key={prop.id}>
              <button className="remove-pick" type="button" aria-label={`Remove ${prop.player}`} onClick={() => onRemove(prop.id)}>×</button>
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
        <div><span>Total picks</span><strong>{pickCount}</strong></div>
        <div><span>Potential multiplier</span><strong>{multiplier.toFixed(1)}x</strong></div>
        <div><span>Potential payout</span><strong>{payout}</strong></div>
        <button type="button" disabled={pickCount === 0}>Place Prediction</button>
      </div>
    </aside>
  )
}

export default PredictionSlip
