import { useState } from 'react'
import CategoryFilters from '../components/CategoryFilters'
import DateSeparator from '../components/DateSeparator'
import GameSection from '../components/GameSection'
import Navbar from '../components/Navbar'
import { propGroups } from '../data/props'
import { Category } from '../types'
import './PropsDashboard.css'

function PropsDashboard() {
  const [selectedCategory, setSelectedCategory] = useState<Category>('All')

  return (
    <div className="dashboard-page">
      <Navbar />
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
                    <GameSection game={game} key={game.id} />
                  ))}
                </section>
              )
            })}
          </div>
        </section>

        <aside className="prediction-slip">
          <h2>Prediction Slip</h2>
          <p>Choose a prediction to add it to your slip.</p>
        </aside>
      </main>
    </div>
  )
}

export default PropsDashboard
