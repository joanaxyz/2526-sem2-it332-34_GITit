import { describe, expect, it } from 'vitest'

import { deriveAchievements } from '@/features/home/utils/achievements'
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
  perfect_clears: 2,
  mastery: 42,
  retry_trends: [],
}

const stats: StatsSummary = {
  skill_profile: [],
  activity_trend: [],
  activity_window: 'month',
  headline: {
    levels_completed: 12,
    finish_rate: { value: 100, numerator: 12, denominator: 12 },
    accuracy: 95,
    hard_tier_clears: { value: 1, scope: 'all' },
    comebacks: { value: 1, scope: 'all' },
    perfect_clears: 2,
    gate_trial_clears: 1,
    hard_gate_trial_clears: 0,
    gitcoins: 250,
    gitcoins_earned: 1200,
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
      'hard-tier-breaker',
      'hard-tier-hunter',
      'gate-breaker',
      'gate-warden',
      'perfectionist',
      'star-collector',
      'rank-glyph-weaver',
      'rank-arcane-adept',
      'rank-archon',
      'comeback-kid',
      'command-cadet',
      'command-captain',
      'sharpshooter',
      'coin-hoarder',
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

  it('tracks rank badges against the rank ladder thresholds', () => {
    const byId = new Map(deriveAchievements(home, stats).map((achievement) => [achievement.id, achievement]))

    expect(byId.get('rank-glyph-weaver')).toMatchObject({ current: 35, target: 35, unlocked: true })
    expect(byId.get('rank-arcane-adept')).toMatchObject({ current: 42, target: 60, unlocked: false })
  })

  it('counts GitCoins earned from play, not the spendable balance', () => {
    const vault = deriveAchievements(home, stats).find((achievement) => achievement.id === 'coin-hoarder')

    expect(vault).toMatchObject({ current: 1000, target: 1000, unlocked: true })
  })

  it('unlocks the gate badges from Challenge Gate trial clears', () => {
    const byId = new Map(deriveAchievements(home, stats).map((achievement) => [achievement.id, achievement]))

    expect(byId.get('gate-breaker')?.unlocked).toBe(true)
    expect(byId.get('gate-warden')).toMatchObject({ current: 0, target: 4, unlocked: false })
  })

  it('unlocks the curriculum badge only for Arcane Spire completion', () => {
    const retiredStory = structuredClone(home)
    retiredStory.completed_stories = ['frostbound-citadel']
    retiredStory.completed_story_slug = 'frostbound-citadel'

    const retiredBadge = deriveAchievements(retiredStory, stats).find(
      (achievement) => achievement.id === 'arcane-spire-master',
    )

    expect(retiredBadge?.unlocked).toBe(false)

    const arcaneSpire = structuredClone(home)
    arcaneSpire.completed_stories = ['arcane-spire']
    arcaneSpire.completed_story_slug = 'arcane-spire'
    const arcaneSpireBadge = deriveAchievements(arcaneSpire, stats).find(
      (achievement) => achievement.id === 'arcane-spire-master',
    )

    expect(arcaneSpireBadge?.unlocked).toBe(true)
  })
})
