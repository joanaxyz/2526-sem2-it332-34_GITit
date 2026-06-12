export type StoreyPracticeMetric = {
  value: number
  numerator: number
  denominator: number
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
