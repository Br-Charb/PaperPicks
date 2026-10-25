import { PlayerProp } from '../types'
import PickToggle from './PickToggle'

interface PropCardProps {
  prop: PlayerProp
}

function PropCard({ prop }: PropCardProps) {
  return (
    <article className="prop-card">
      <h3>{prop.player}</h3>
      <p className="prop-line">
        {prop.category === 'Game Outcome' ? 'To win by' : prop.category}: <strong>{prop.line}</strong>
      </p>
      <div className="prop-meta">
        <span>{prop.matchup}</span>
        <span>{prop.time}</span>
      </div>
      <PickToggle label={`Choose over or under for ${prop.player}`} />
    </article>
  )
}

export default PropCard
