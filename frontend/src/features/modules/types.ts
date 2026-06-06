export type ModulePracticeMetric = {
  value: number
  numerator: number
  denominator: number
}

export type FoundationTopic = {
  id: number
  slug: string
  title: string
  summary: string
  body: string
  icon: string
  cards: Array<{
    title: string
    body: string
    command?: string
  }>
  sort_order: number
}

export type LearningModule = {
  id: number
  slug: string
  number: number
  title: string
  description: string
  sort_order: number
  command_topic_count: number
  workflow_scenario_count: number
  practice_completion?: ModulePracticeMetric
}
