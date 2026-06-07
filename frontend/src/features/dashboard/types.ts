export type RateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

export type TowerKpis = Record<string, {
  scr: RateMetric
  hlcr: RateMetric
  rta: RateMetric
  arc: RateMetric
}>

export type DashboardSummary = {
  kpis: Record<'practice_completion' | 'scr' | 'arc' | 'car' | 'hlcr' | 'rta', RateMetric>
  tower_kpis: TowerKpis
  module_kpis?: TowerKpis
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
    practice_kind: 'command_drill' | 'workflow_scenario'
    practice_title: string
    attempts: number
    retries: number
    label: string
  }>
}
