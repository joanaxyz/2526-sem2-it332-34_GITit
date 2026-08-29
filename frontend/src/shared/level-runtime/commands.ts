/** Shared command text helpers for challenge/adventure runtime screens. */
export function isExitCommand(command: string) {
  return command.trim().toLowerCase() === 'exit'
}
