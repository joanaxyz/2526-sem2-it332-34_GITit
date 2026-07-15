import { describe, expect, it } from 'vitest'

import { deriveAchievements, latestAchievement } from '@/features/home/utils/achievements'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'

const home: HomeSummary = {
  kpis: {
    scr: { value: 100, numerator: 1, denominator: 1 },
    arc: { value: 0, numerator: 0, denominator: 1 },
    hlcr: { value: 0, numerator: 0, denominator: 1 },
  },
  chapter_kpis: {},
  counts: {
    started: 12,
    completed: 12,
    failed: 0,
    abandoned: 0,
  },
  completed_stories: [],
  completed_story_slug: null,
  streak: {
    current: 4,
    longest: 4,
    last_completed_on: '2026-07-12',
  },
  perfect_clears: 2,
  mastery: 42,
  retry_trends: [],
}

const stats: StatsSummary = {
  skill_profile: [],
  activity_trend: [],
  headline: {
    levels_completed: 12,
    finish_rate: { value: 100, numerator: 12, denominator: 12 },
    accuracy: 95,
    boss_floors: { value: 1, scope: 'all' },
    comebacks: { value: 1, scope: 'all' },
    perfect_clears: 2,
    day_streak: 4,
    longest_streak: 4,
    gitcoins: 250,
    commands_run: 99,
  },
}

describe('deriveAchievements', () => {
  it('returns the full image-backed achievement catalog', () => {
    const achievements = deriveAchievements(home, stats)

    expect(achievements).toHaveLength(19)
    expect(achievements.map((achievement) => achievement.id)).toEqual([
      'first-clear',
      'level-adept',
      'level-veteran',
      'level-champion',
      'streak-spark',
      'weeklong-flame',
      'fortnight-blaze',
      'perfectionist',
      'star-collector',
      'boss-slayer',
      'boss-reaper',
      'comeback-kid',
      'command-cadet',
      'command-captain',
      'coin-hoarder',
      'sharpshooter',
      'story-climber',
      'story-sentinel',
      'arcane-spire-master',
    ])
    expect(achievements.every((achievement) => achievement.imageSrc.length > 0)).toBe(true)
  })

  it('keeps accuracy achievements locked until enough commands have run', () => {
    const achievements = deriveAchievements(home, stats)

    expect(achievements.find((achievement) => achievement.id === 'sharpshooter')).toMatchObject({
      current: 90,
      target: 90,
      unlocked: false,
    })
  })

  it('uses the highest-value unlocked badge as the latest achievement stand-in', () => {
    const achievements = deriveAchievements(home, stats)

    expect(latestAchievement(achievements)?.id).toBe('boss-slayer')
  })
})
