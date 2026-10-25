import { Game, PickChoice, SelectedPicks } from '../types'
import PropCard from './PropCard'

interface GameSectionProps {
  game: Game
  selectedPicks: SelectedPicks
  onPick: (propId: string, choice: PickChoice) => void
}

function GameSection({ game, selectedPicks, onPick }: GameSectionProps) {
  return (
    <section className="game-section" aria-labelledby={`game-${game.id}`}>
      <header className="game-header">
        <div className="matchup-badge" aria-hidden="true">{game.matchup.split(' @ ').map((team) => team[0]).join('')}</div>
        <h2 id={`game-${game.id}`}>{game.matchup}</h2>
        <time>{game.time}</time>
      </header>
      <div className="prop-grid">
        {game.props.map((prop) => (
          <PropCard prop={prop} choice={selectedPicks[prop.id]} onPick={onPick} key={prop.id} />
        ))}
      </div>
    </section>
  )
}

export default GameSection
