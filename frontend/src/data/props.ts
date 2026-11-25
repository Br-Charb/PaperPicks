import { DateGroup } from '../types'

function futureDate(daysAhead: number, hour24: number, minute: number): Date {
  const date = new Date()
  date.setDate(date.getDate() + daysAhead)
  date.setHours(hour24, minute, 0, 0)
  return date
}

function formatDateLabel(date: Date): string {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${month}/${day}/${date.getFullYear()}`
}

const thursdayKickoff = futureDate(1, 20, 15)
const sundayEarlyKickoff = futureDate(3, 13, 0)
const sundayAfternoonKickoff = futureDate(3, 16, 5)
const sundayNightKickoff = futureDate(3, 20, 20)

export const propGroups: DateGroup[] = [
  {
    date: formatDateLabel(thursdayKickoff),
    games: [
      {
        id: 'buf-kc',
        matchup: 'BUF @ KC',
        kickoff: thursdayKickoff.toISOString(),
        props: [
          { id: 'james-cook-rush', player: 'James Cook', category: 'Rushing Yards', line: '72.5', matchup: 'BUF @ KC', time: '8:15 PM' },
          { id: 'josh-allen-pass', player: 'Josh Allen', category: 'Passing Yards', line: '275.5', matchup: 'BUF @ KC', time: '8:15 PM' },
          { id: 'patrick-mahomes-pass', player: 'Patrick Mahomes', category: 'Passing Yards', line: '268.5', matchup: 'BUF @ KC', time: '8:15 PM' },
          { id: 'travis-kelce-receive', player: 'Travis Kelce', category: 'Receiving Yards', line: '64.5', matchup: 'BUF @ KC', time: '8:15 PM' },
        ],
      },
    ],
  },
  {
    date: formatDateLabel(sundayEarlyKickoff),
    games: [
      {
        id: 'dal-sf',
        matchup: 'DAL @ SF',
        kickoff: sundayEarlyKickoff.toISOString(),
        props: [
          { id: 'ceedee-lamb-receive', player: 'CeeDee Lamb', category: 'Receiving Yards', line: '78.5', matchup: 'DAL @ SF', time: '1:00 PM' },
          { id: 'christian-mccaffrey-rush', player: 'Christian McCaffrey', category: 'Rushing Yards', line: '81.5', matchup: 'DAL @ SF', time: '1:00 PM' },
          { id: 'dak-prescott-pass', player: 'Dak Prescott', category: 'Passing Yards', line: '252.5', matchup: 'DAL @ SF', time: '1:00 PM' },
          { id: 'george-kittle-td', player: 'George Kittle', category: 'TDs', line: '0.5', matchup: 'DAL @ SF', time: '1:00 PM' },
        ],
      },
      {
        id: 'bal-tb',
        matchup: 'BAL @ TB',
        kickoff: sundayAfternoonKickoff.toISOString(),
        props: [
          { id: 'baker-mayfield-pass', player: 'Baker Mayfield', category: 'Passing Yards', line: '246.5', matchup: 'BAL @ TB', time: '4:05 PM' },
          { id: 'derrick-henry-rush', player: 'Derrick Henry', category: 'Rushing Yards', line: '85.5', matchup: 'BAL @ TB', time: '4:05 PM' },
          { id: 'lamar-jackson-pass', player: 'Lamar Jackson', category: 'Passing Yards', line: '247.5', matchup: 'BAL @ TB', time: '4:05 PM' },
          { id: 'zay-flowers-receive', player: 'Zay Flowers', category: 'Receiving Yards', line: '58.5', matchup: 'BAL @ TB', time: '4:05 PM' },
        ],
      },
      {
        id: 'gb-pit',
        matchup: 'GB @ PIT',
        kickoff: sundayNightKickoff.toISOString(),
        props: [
          { id: 'dk-metcalf-receive', player: 'DK Metcalf', category: 'Receiving Yards', line: '67.5', matchup: 'GB @ PIT', time: '8:20 PM' },
          { id: 'green-bay-outcome', player: 'Green Bay Packers', category: 'Game Outcome', line: '3.5', matchup: 'GB @ PIT', time: '8:20 PM' },
          { id: 'jordan-love-pass', player: 'Jordan Love', category: 'Passing Yards', line: '241.5', matchup: 'GB @ PIT', time: '8:20 PM' },
          { id: 'kenneth-gainwell-rush', player: 'Kenneth Gainwell', category: 'Rushing Yards', line: '54.5', matchup: 'GB @ PIT', time: '8:20 PM' },
        ],
      },
    ],
  },
]

export const allProps = propGroups.flatMap((dateGroup) => dateGroup.games.flatMap((game) => game.props))
