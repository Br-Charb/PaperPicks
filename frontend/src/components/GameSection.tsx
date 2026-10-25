import { Game } from '../types'
import PropCard from './PropCard'

interface GameSectionProps {
  game: Game
}

function GameSection({ game }: GameSectionProps) {
  return (
    <section className="game-section" aria-labelledby={`game-${game.id}`}>
      <header className="game-header">
        <div className="matchup-badge" aria-hidden="true">{game.matchup.split(' @ ').map((team) => team[0]).join('')}</div>
        <h2 id={`game-${game.id}`}>{game.matchup}</h2>
        <time>{game.time}</time>
      </header>
      <div className="prop-grid">
        {game.props.map((prop) => (
          <PropCard prop={prop} key={prop.id} />
        ))}
      </div>
    </section>
  )
}

export default GameSection
