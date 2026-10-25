import { Game, PickChoice, SelectedPicks } from '../types'
import KickoffCountdown from './KickoffCountdown'
import PropCard from './PropCard'

interface GameSectionProps {
  game: Game
  selectedPicks: SelectedPicks
  onPick: (propId: string, choice: PickChoice) => void
}

function GameSection({ game, selectedPicks, onPick }: GameSectionProps) {
  const kickoff = new Date(game.kickoff)
  const gameDate = kickoff.toLocaleDateString('en-US', { timeZone: 'America/New_York' })
  const gameTime = kickoff.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    timeZone: 'America/New_York',
  })

  return (
    <section className="game-section" aria-labelledby={`game-${game.id}`}>
      <header className="game-header">
        <div className="matchup-badge" aria-hidden="true">{game.matchup.split(' @ ').map((team) => team[0]).join('')}</div>
        <h2 id={`game-${game.id}`}>{game.matchup}</h2>
        <span className="game-divider" aria-hidden="true">|</span>
        <KickoffCountdown kickoff={game.kickoff} />
        <time className="game-schedule" dateTime={game.kickoff}>{gameDate} @ {gameTime}</time>
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
