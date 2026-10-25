export function hasKickedOff(kickoff: string, currentTime: number) {
  return new Date(kickoff).getTime() <= currentTime
}
