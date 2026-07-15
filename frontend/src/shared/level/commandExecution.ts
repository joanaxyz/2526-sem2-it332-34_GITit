import type { CommandExecutionPayload } from '@/shared/level/types'

/**
 * Attach the live run/attempt revision that the command was simulated against.
 *
 * The UI still executes commands optimistically for instant feedback, but the
 * backend compares this value against the locked run row before accepting the
 * payload. That cheaply rejects stale double-submits without replaying the full
 * simulator on every request.
 */
export function withClientRunRevision(
  execution: CommandExecutionPayload,
  revision: number,
): CommandExecutionPayload {
  return { ...execution, client_run_revision: revision }
}
