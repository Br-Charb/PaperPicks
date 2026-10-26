export type Category = 'All' | 'Game Outcome' | 'Passing Yards' | 'Rushing Yards' | 'Receiving Yards' | 'TDs'

export type PickChoice = 'over' | 'under'

export interface PlayerProp {
  id: string
  player: string
  category: Exclude<Category, 'All'>
  line: string
  matchup: string
  time: string
}

export interface Game {
  id: string
  matchup: string
  kickoff: string
  props: PlayerProp[]
}

export interface DateGroup {
  date: string
  games: Game[]
}

export type SelectedPicks = Record<string, PickChoice>

export interface User {
  id: number
  username: string
  email: string
  role: 'member' | 'admin' | string
  balance: number
  account_status: 'active' | 'suspended' | string
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}
