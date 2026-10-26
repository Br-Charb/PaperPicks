import { useEffect, useState } from 'react'
import CategoryFilters from '../components/CategoryFilters'
import DateSeparator from '../components/DateSeparator'
import GameSection from '../components/GameSection'
import Navbar from '../components/Navbar'
import PredictionSlip from '../components/PredictionSlip'
import { allProps, propGroups } from '../data/props'
import { Category, PickChoice, SelectedPicks } from '../types'
import { hasKickedOff } from '../utils/kickoff'
import './PropsDashboard.css'

const kickoffByProp: Record<string, string> = Object.fromEntries(
  propGroups.flatMap((dateGroup) =>
    dateGroup.games.flatMap((game) => game.props.map((prop) => [prop.id, game.kickoff])),
  ),
)

// Drops picks whose game has kicked off
function removeLockedPicks(picks: SelectedPicks, currentTime: number): SelectedPicks {
  const openPicks = Object.fromEntries(
    Object.entries(picks).filter(([propId]) => !hasKickedOff(kickoffByProp[propId], currentTime)),
  )
  return Object.keys(openPicks).length === Object.keys(picks).length ? picks : openPicks
}

interface PropsDashboardProps {
  onNavigate?: (path: string) => void
}

function PropsDashboard({ onNavigate }: PropsDashboardProps) {
  const [selectedCategory, setSelectedCategory] = useState<Category>('All')
  const [selectedPicks, setSelectedPicks] = useState<SelectedPicks>({})
  const [currentTime, setCurrentTime] = useState(() => Date.now())

  useEffect(() => {
    const timer = window.setInterval(() => {
      const now = Date.now()
      setCurrentTime(now)
      setSelectedPicks((current) => removeLockedPicks(current, now))
    }, 1000)
    return () => window.clearInterval(timer)
  }, [])

  function handlePick(propId: string, choice: PickChoice) {
    if (selectedPicks[propId] === choice) {
      removePick(propId)
      return
    }
    setSelectedPicks((current) => ({ ...current, [propId]: choice }))
  }

  function removePick(propId: string) {
    setSelectedPicks((current) => {
      const nextPicks = { ...current }
      delete nextPicks[propId]
      return nextPicks
    })
  }

  const selectedProps = allProps.filter((prop) => selectedPicks[prop.id])

  return (
    <div className="dashboard-page">
      <Navbar onNavigate={onNavigate} />
      <main className="dashboard-layout">
        <section className="props-browser" aria-labelledby="props-title">
          <header className="page-heading">
            <p>NFL</p>
            <h1 id="props-title">NFL Props</h1>
            <span>Browse upcoming NFL games and player props. Make your predictions with virtual currency.</span>
          </header>

          <CategoryFilters selected={selectedCategory} onChange={setSelectedCategory} />

          <div className="prop-sections">
            {propGroups.map((dateGroup) => {
              const visibleGames = dateGroup.games
                .map((game) => ({
                  ...game,
                  props: game.props.filter((prop) => selectedCategory === 'All' || prop.category === selectedCategory),
                }))
                .filter((game) => game.props.length > 0)

              if (visibleGames.length === 0) {
                return null
              }

              return (
                <section className="date-group" key={dateGroup.date}>
                  <DateSeparator date={dateGroup.date} />
                  {visibleGames.map((game) => (
                    <GameSection
                      game={game}
                      locked={hasKickedOff(game.kickoff, currentTime)}
                      selectedPicks={selectedPicks}
                      onPick={handlePick}
                      key={game.id}
                    />
                  ))}
                </section>
              )
            })}
          </div>
        </section>

        <PredictionSlip
          props={selectedProps}
          selectedPicks={selectedPicks}
          onPick={handlePick}
          onRemove={removePick}
        />
      </main>
    </div>
  )
}

export default PropsDashboard
