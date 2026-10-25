import { useEffect, useState } from 'react'

interface KickoffCountdownProps {
  kickoff: string
}

function getTimeRemaining(kickoff: string, currentTime: number) {
  const difference = new Date(kickoff).getTime() - currentTime

  if (difference <= 0) {
    return 'Live'
  }

  const totalSeconds = Math.ceil(difference / 1000)
  const days = Math.floor(totalSeconds / 86400)
  const hours = Math.floor((totalSeconds % 86400) / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  if (days > 0) {
    return `${days}d ${hours}h`
  }

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }

  return `${minutes}m ${seconds}s`
}

function KickoffCountdown({ kickoff }: KickoffCountdownProps) {
  const [currentTime, setCurrentTime] = useState<number | null>(null)

  useEffect(() => {
    const timer = window.setInterval(() => setCurrentTime(Date.now()), 1000)
    return () => window.clearInterval(timer)
  }, [])

  const timeRemaining = currentTime === null ? '--' : getTimeRemaining(kickoff, currentTime)

  return (
    <span className="game-countdown">
      Time to game <strong>{timeRemaining}</strong>
    </span>
  )
}

export default KickoffCountdown
