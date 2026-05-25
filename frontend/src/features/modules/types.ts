export type ModulePracticeMetric = {
  value: number
  numerator: number
  denominator: number
}

export type LessonSummary = {
  id: number
  slug: string
  title: string
  subtitle: string
  sort_order: number
  is_complete: boolean
  scenario_count: number
}

export type LearningModule = {
  id: number
  slug: string
  number: number
  title: string
  description: string
  is_orientation: boolean
  sort_order: number
  lesson_count: number
  scenario_count: number
  practice_completion?: ModulePracticeMetric
  lessons: LessonSummary[]
}

export type LessonDetail = LessonSummary & {
  content_html: string
  scoped_css: string
  interaction_steps: string[]
  module: {
    id: number
    slug: string
    number: number
    title: string
    is_orientation: boolean
  }
  unit?: {
    id: number
    slug: string
    number: number
    title: string
    is_orientation: boolean
  }
}

export type OrientationStatus = {
  orientation_complete: boolean
  lessons: Array<{
    lesson_id: number
    highest_step_seen: number
    completed_at: string | null
    is_complete: boolean
  }>
}
