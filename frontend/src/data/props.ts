import { DateGroup } from '../types'

export const propGroups: DateGroup[] = [
  {
    date: '10/24/2026',
    games: [
      {
        id: 'buf-kc',
        matchup: 'BUF @ KC',
        time: '4:25 PM',
        props: [
          { id: 'james-cook-rush', player: 'James Cook', category: 'Rushing Yards', line: '72.5', matchup: 'BUF @ KC', time: '4:25 PM' },
          { id: 'josh-allen-pass', player: 'Josh Allen', category: 'Passing Yards', line: '275.5', matchup: 'BUF @ KC', time: '4:25 PM' },
          { id: 'patrick-mahomes-pass', player: 'Patrick Mahomes', category: 'Passing Yards', line: '268.5', matchup: 'BUF @ KC', time: '4:25 PM' },
          { id: 'travis-kelce-receive', player: 'Travis Kelce', category: 'Receiving Yards', line: '64.5', matchup: 'BUF @ KC', time: '4:25 PM' },
        ],
      },
      {
        id: 'dal-sf',
        matchup: 'DAL @ SF',
        time: '8:20 PM',
        props: [
          { id: 'ceedee-lamb-receive', player: 'CeeDee Lamb', category: 'Receiving Yards', line: '78.5', matchup: 'DAL @ SF', time: '8:20 PM' },
          { id: 'christian-mccaffrey-rush', player: 'Christian McCaffrey', category: 'Rushing Yards', line: '81.5', matchup: 'DAL @ SF', time: '8:20 PM' },
          { id: 'dak-prescott-pass', player: 'Dak Prescott', category: 'Passing Yards', line: '252.5', matchup: 'DAL @ SF', time: '8:20 PM' },
          { id: 'george-kittle-td', player: 'George Kittle', category: 'TDs', line: '0.5', matchup: 'DAL @ SF', time: '8:20 PM' },
        ],
      },
    ],
  },
  {
    date: '10/25/2026',
    games: [
      {
        id: 'bal-tb',
        matchup: 'BAL @ TB',
        time: '1:00 PM',
        props: [
          { id: 'baker-mayfield-pass', player: 'Baker Mayfield', category: 'Passing Yards', line: '246.5', matchup: 'BAL @ TB', time: '1:00 PM' },
          { id: 'derrick-henry-rush', player: 'Derrick Henry', category: 'Rushing Yards', line: '85.5', matchup: 'BAL @ TB', time: '1:00 PM' },
          { id: 'lamar-jackson-pass', player: 'Lamar Jackson', category: 'Passing Yards', line: '247.5', matchup: 'BAL @ TB', time: '1:00 PM' },
          { id: 'zay-flowers-receive', player: 'Zay Flowers', category: 'Receiving Yards', line: '58.5', matchup: 'BAL @ TB', time: '1:00 PM' },
        ],
      },
      {
        id: 'gb-pit',
        matchup: 'GB @ PIT',
        time: '4:05 PM',
        props: [
          { id: 'dk-metcalf-receive', player: 'DK Metcalf', category: 'Receiving Yards', line: '67.5', matchup: 'GB @ PIT', time: '4:05 PM' },
          { id: 'green-bay-outcome', player: 'Green Bay Packers', category: 'Game Outcome', line: '3.5', matchup: 'GB @ PIT', time: '4:05 PM' },
          { id: 'jordan-love-pass', player: 'Jordan Love', category: 'Passing Yards', line: '241.5', matchup: 'GB @ PIT', time: '4:05 PM' },
          { id: 'kenneth-gainwell-rush', player: 'Kenneth Gainwell', category: 'Rushing Yards', line: '54.5', matchup: 'GB @ PIT', time: '4:05 PM' },
        ],
      },
    ],
  },
]

export const allProps = propGroups.flatMap((dateGroup) => dateGroup.games.flatMap((game) => game.props))
