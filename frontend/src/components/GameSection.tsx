import { Game } from '../types'

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
          <article className="prop-card" key={prop.id}>
            <h3>{prop.player}</h3>
            <p className="prop-line">
              {prop.category === 'Game Outcome' ? 'To win by' : prop.category}: <strong>{prop.line}</strong>
            </p>
            <div className="prop-meta">
              <span>{prop.matchup}</span>
              <span>{prop.time}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}

export default GameSection
