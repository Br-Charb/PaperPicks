import { useCallback, useEffect, useMemo, useState } from 'react'
import { getAvailableProps } from '../api/props'
import CategoryFilters from '../components/CategoryFilters'
import DateSeparator from '../components/DateSeparator'
import GameSection from '../components/GameSection'
import Navbar from '../components/Navbar'
import PredictionSlip from '../components/PredictionSlip'
import ToastBanner from '../components/ToastBanner'
import { useAuth } from '../context/useAuth'
import { propGroups as fallbackPropGroups } from '../data/props'
import { Category, DateGroup, PickChoice, SelectedPicks, ToastMessage } from '../types'
import { hasKickedOff } from '../utils/kickoff'
import './PropsDashboard.css'

// Drops picks whose game has kicked off
function removeLockedPicks(
  picks: SelectedPicks,
  kickoffByProp: Record<string, string>,
  currentTime: number,
): SelectedPicks {
  const openPicks = Object.fromEntries(
    Object.entries(picks).filter(([propId]) => {
      const kickoff = kickoffByProp[propId]
      return kickoff ? !hasKickedOff(kickoff, currentTime) : false
    }),
  )
  return Object.keys(openPicks).length === Object.keys(picks).length ? picks : openPicks
}

interface PropsDashboardProps {
  onNavigate?: (path: string) => void
}

function PropsDashboard({ onNavigate }: PropsDashboardProps) {
  const { user } = useAuth()
  const [selectedCategory, setSelectedCategory] = useState<Category>('All')
  const [selectedPicks, setSelectedPicks] = useState<SelectedPicks>({})
  const [currentTime, setCurrentTime] = useState(() => Date.now())
  const [toast, setToast] = useState<ToastMessage | null>(null)
  const [propGroups, setPropGroups] = useState<DateGroup[]>(fallbackPropGroups)

  useEffect(() => {
    if (!user) {
      return
    }

    let active = true
    async function loadProps() {
      try {
        const liveGroups = await getAvailableProps()
        if (active && liveGroups.length > 0) {
          setPropGroups(liveGroups)
        }
      } catch {
        // Keep fallback demo props if backend props are unavailable
      }
    }

    void loadProps()
    return () => {
      active = false
    }
  }, [user])

  const kickoffByProp = useMemo(
    () =>
      Object.fromEntries(
        propGroups.flatMap((dateGroup) =>
          dateGroup.games.flatMap((game) =>
            game.props.map((prop) => [prop.id, game.kickoff]),
          ),
        ),
      ),
    [propGroups],
  )

  const allProps = useMemo(
    () =>
      propGroups.flatMap((dateGroup) =>
        dateGroup.games.flatMap((game) => game.props),
      ),
    [propGroups],
  )

  useEffect(() => {
    const timer = window.setInterval(() => {
      const now = Date.now()
      setCurrentTime(now)
      setSelectedPicks((current) => removeLockedPicks(current, kickoffByProp, now))
    }, 1000)
    return () => window.clearInterval(timer)
  }, [kickoffByProp])

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

  const clearPicks = useCallback(() => {
    setSelectedPicks({})
  }, [])

  const showToast = useCallback((nextToast: Omit<ToastMessage, 'id'>) => {
    setToast({ ...nextToast, id: Date.now() })
  }, [])

  const dismissToast = useCallback(() => {
    setToast(null)
  }, [])

  const selectedProps = allProps.filter((prop) => selectedPicks[prop.id])

  return (
    <div className="dashboard-page">
      <Navbar onNavigate={onNavigate} />
      <ToastBanner toast={toast} onDismiss={dismissToast} />
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
          onClear={clearPicks}
          onNotify={showToast}
        />
      </main>
    </div>
  )
}

export default PropsDashboard
