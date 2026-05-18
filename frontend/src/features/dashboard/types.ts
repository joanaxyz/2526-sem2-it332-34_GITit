export type RateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

export type DashboardSummary = {
  kpis: Record<'orientation_completion' | 'scr' | 'arc' | 'car' | 'hlcr' | 'rta' | 'sar' | 'review_scr', RateMetric>
  counts: {
    started: number
    completed: number
    failed: number
    abandoned: number
    review_started: number
  }
  streak: {
    current: number
    longest: number
    last_completed_on: string | null
  }
  first_attempt_stars: number
  retry_trends: Array<{
    scenario_id: number
    scenario_title: string
    attempts: number
    retries: number
    label: string
  }>
}
