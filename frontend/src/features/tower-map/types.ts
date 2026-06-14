export type StoreyLevelMetric = {
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
  level_completion?: StoreyLevelMetric
  chest_rewards?: ChestReward[]
}
