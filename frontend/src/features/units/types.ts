export type LessonKind = 'orientation' | 'content' | 'scenario'

export type LessonSummary = {
  id: number
  slug: string
  title: string
  subtitle: string
  kind: LessonKind
  sort_order: number
  is_complete: boolean
}

export type LearningUnit = {
  id: number
  slug: string
  number: number
  title: string
  description: string
  is_orientation: boolean
  sort_order: number
  lesson_count: number
  scenario_count: number
  lessons: LessonSummary[]
}

export type LessonDetail = LessonSummary & {
  overview_html: string
  scoped_css: string
  interaction_steps: string[]
  unit: {
    id: number
    slug: string
    number: number
    title: string
    is_orientation: boolean
  }
}

export type OrientationStatus = {
  gate_satisfied: boolean
  lessons: Array<{
    lesson_id: number
    highest_step_seen: number
    completed_at: string | null
    is_complete: boolean
  }>
}
