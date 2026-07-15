export type RateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

export type ChapterKpis = Record<string, {
  scr: RateMetric
  hlcr: RateMetric
  arc: RateMetric
}>

export type HomeSummary = {
  kpis: Record<'scr' | 'arc' | 'hlcr', RateMetric>
  chapter_kpis: ChapterKpis
  counts: {
    started: number
    completed: number
    failed: number
    abandoned: number
  }
  completed_story_slug?: string | null
  completed_stories?: string[]
  streak: {
    current: number
    longest: number
    last_completed_on: string | null
  }
  perfect_clears: number
  /** 0-100 blend of adventure solve depth + challenge clear ratio; rank is expressed directly in terms of this. */
  mastery: number
  retry_trends: Array<{
    level_title: string
    attempts: number
    retries: number
    label: string
  }>
}
