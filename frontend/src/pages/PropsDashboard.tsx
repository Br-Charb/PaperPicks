import { useState } from 'react'
import CategoryFilters from '../components/CategoryFilters'
import DateSeparator from '../components/DateSeparator'
import GameSection from '../components/GameSection'
import Navbar from '../components/Navbar'
import PredictionSlip from '../components/PredictionSlip'
import { allProps, propGroups } from '../data/props'
import { Category, PickChoice, SelectedPicks } from '../types'
import './PropsDashboard.css'

interface PropsDashboardProps {
  onNavigate?: (path: string) => void
}

function PropsDashboard({ onNavigate }: PropsDashboardProps) {
  const [selectedCategory, setSelectedCategory] = useState<Category>('All')
  const [selectedPicks, setSelectedPicks] = useState<SelectedPicks>({})

  function handlePick(propId: string, choice: PickChoice) {
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
                    <GameSection game={game} selectedPicks={selectedPicks} onPick={handlePick} key={game.id} />
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
