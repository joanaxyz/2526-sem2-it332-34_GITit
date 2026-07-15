export type Story = {
  id: number
  slug: string
  title: string
  summary: string
  sort_order: number
  is_published: boolean
  completed: boolean
  owned: boolean
  world_slug: string
  difficulty: 'beginner' | 'advanced' | 'expert'
  prerequisite_story: { slug: string; title: string; completed: boolean } | null
  locked: boolean
  lock_reason: string
  price: number
}
export type ChapterLevelMetric = {
  value: number
  numerator: number
  denominator: number
}

export type ChestReward = {
  threshold: number
  coins: number
}

export type LearningChapter = {
  id: number
  slug: string
  number: number
  title: string
  description: string
  sort_order: number
  is_playable: boolean
  story: { id: number; slug: string; title: string; world_slug: string } | null
  locked: boolean
  lock_reason: string
  command_skill_count: number
  challenge_count: number
  adventure_level_count: number
  level_completion?: ChapterLevelMetric
  /** Fixed, runtime-computed reward schedule - the same for every chapter. */
  chest_schedule: ChestReward[]
}
