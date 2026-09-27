/**
 * Shell identity for the workspace terminals: the signed-in username and
 * nothing else. Host and working-directory segments only crowded the prompt
 * out of the panel, and the command line is the part learners read.
 * The fallback only covers missing data (guest sessions, legacy runs).
 */
export function terminalPrompt(username?: string | null): string {
  return (username || 'adventurer').toLowerCase().replace(/\s+/g, '-')
}
