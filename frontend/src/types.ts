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

export interface BalanceInfo {
  balance: number
  can_restore: boolean
  restore_amount: number
}

export interface BalanceRestoreResult {
  message: string
  balance: number
  credited_amount: number
}

export interface BetLegCreatePayload {
  prop_id: number
  pick: PickChoice
}

export interface BetCreatePayload {
  wager: number
  legs: BetLegCreatePayload[]
}

export interface BetLegRecord {
  id: number
  prop_id: number
  player_name: string
  stat_category: string
  matchup: string
  line_snapshot: number
  pick: PickChoice
  status: string
}

export interface BetRecord {
  id: number
  user_id: number
  wager: number
  multiplier: number
  potential_payout: number
  actual_payout: number
  status: string
  created_at: string
  settled_at: string | null
  legs: BetLegRecord[]
}

export interface BetPlacementResult {
  bet: BetRecord
  balance: number
}

export interface ToastMessage {
  id: number
  type: 'success' | 'error' | 'warning'
  title: string
  message: string
}


