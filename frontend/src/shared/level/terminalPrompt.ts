export type TerminalPrompt = {
  user: string
  host: string
  cwd: string
}

/**
 * Shell identity for the workspace terminals, derived from live data:
 * the signed-in username, the story slug, and the level's repo slug.
 * Fallbacks only cover missing data (guest sessions, legacy runs).
 */
export function terminalPrompt({
  username,
  host,
  repo,
}: {
  username?: string | null
  host?: string | null
  repo?: string | null
}): TerminalPrompt {
  return {
    user: (username || 'blue').toLowerCase().replace(/\s+/g, '-'),
    host: host || 'arcane-spire',
    cwd: `~/${repo || 'repo'}`,
  }
}
