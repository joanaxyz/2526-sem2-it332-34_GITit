import type { ChallengeStatus, ChallengeTrialAccess } from '@/features/challenges/types'
import type { BookPage } from '@/features/story-map/components/book/bookTypes'
import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

type LevelCompletionSummary = {
  stars: number
  counted_action_total: number
  completed_at: string
}

type AdventureSummary = {
  item_type: 'adventure'
  id: number
  slug: string
  title: string
  command: string
  locked: boolean
  lock_reason: string
  completion: LevelCompletionSummary | null
  // Stable across re-runs: true once the level has ever been passed. Drives
  // the challenge gate and progress so a post-pass replay can't relock anything.
  is_passed: boolean
}

export type AdventureLevelSummary = AdventureSummary

export type ChallengeSummary = {
  item_type: 'challenge'
  id: number
  slug: string
  title: string
  summary: string
  narrative: string
  status: ChallengeStatus
  completed: boolean
  locked: boolean
  trials: ChallengeTrialAccess[]
}

type ChapterLessonSummary = {
  item_type: 'lesson'
  id: number
  slug: string
  title: string
  summary: string
  // Pages ship inline (lessons are small), so opening the reader needs no fetch.
  pages: BookPage[]
}

export type ChapterContentOverview = {
  chapter_id: number
  adventures: AdventureSummary[]
  lessons: ChapterLessonSummary[]
  challenges: ChallengeSummary[]
}

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
  difficulty: ApiSchemas['DifficultyEnum']
  prerequisite_story: { slug: string; title: string; completed: boolean } | null
  locked: boolean
  lock_reason: string
  price: number
}
type ChapterLevelMetric = {
  value: number
  numerator: number
  denominator: number
}

type ChestReward = {
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
