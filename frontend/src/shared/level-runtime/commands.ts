/** Shared command text helpers for challenge/adventure runtime screens. */
export function isExitCommand(command: string) {
  return command.trim().toLowerCase() === 'exit'
}

/** Only Git commands participate in the workspace's command choreography. */
export function isGitCommand(command: string) {
  return /^git(?:\s|$)/.test(command.trim())
}
