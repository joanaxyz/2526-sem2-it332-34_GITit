export type ScaffoldTriggerEvent = {
  event_type: 'scaffold_trigger'
  trigger: 'T1' | 'T2' | 'T3'
  difficulty: string
  counted_commands_used: number
  budget_consumed_pct: number
  timestamp: string
}

/**
 * Emits a scaffold trigger event for analytics purposes.
 * This log has zero effect on session state, CAR, star eligibility, or any displayed value.
 */
export function logScaffoldTrigger(event: Omit<ScaffoldTriggerEvent, 'event_type' | 'timestamp'>): void {
  const entry: ScaffoldTriggerEvent = {
    event_type: 'scaffold_trigger',
    ...event,
    timestamp: new Date().toISOString(),
  }
  // Write to console in development; a future analytics endpoint can be wired here.
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    console.debug('[scaffold]', entry)
  }
}
