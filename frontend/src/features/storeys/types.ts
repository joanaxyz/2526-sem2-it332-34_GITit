export type StoreyPracticeMetric = {
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

export type ChestReward = {
  threshold: number
  coins: number
}

export type LearningStorey = {
  id: number
  slug: string
  number: number
  title: string
  description: string
  sort_order: number
  command_skill_count: number
  challenge_count: number
  practice_completion?: StoreyPracticeMetric
  chest_rewards?: ChestReward[]
}
