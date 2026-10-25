import { PickChoice, PlayerProp } from '../types'
import PickToggle from './PickToggle'

interface PropCardProps {
  prop: PlayerProp
  choice?: PickChoice
  onPick: (propId: string, choice: PickChoice) => void
}

function PropCard({ prop, choice, onPick }: PropCardProps) {
  return (
    <article className={`prop-card${choice ? ' selected' : ''}`}>
      <h3>{prop.player}</h3>
      <p className="prop-line">
        {prop.category === 'Game Outcome' ? 'To win by' : prop.category}: <strong>{prop.line}</strong>
      </p>
      <div className="prop-meta">
        <span>{prop.matchup}</span>
        <span>{prop.time}</span>
      </div>
      <PickToggle
        value={choice}
        label={`Choose over or under for ${prop.player}`}
        onChange={(nextChoice) => onPick(prop.id, nextChoice)}
      />
    </article>
  )
}

export default PropCard
