import {
  Castle,
  Coins,
  Crosshair,
  Crown,
  Flame,
  Medal,
  Sparkles,
  Star,
  Swords,
  TerminalSquare,
  type LucideIcon,
} from 'lucide-react'

import { highestChapterTouched } from '@/shared/progress/rank'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { ACHIEVEMENT_IMAGES, type AchievementImageId } from '@/features/home/utils/achievementImages'

/**
 * Client-derived achievement ledger. There is no achievements table in the
 * backend (yet) - every badge below is computed deterministically from the
 * home + stats summaries, so the set stays consistent across reloads.
 * `points` are cosmetic gamerscore-style stars, NOT GitCoins (coins only
 * ever come from chapter chests).
 */
export type Achievement = {
  id: AchievementImageId
  title: string
  desc: string
  Icon: LucideIcon
  imageSrc: string
  color: string
  points: number
  current: number
  target: number
  unlocked: boolean
}

export function deriveAchievements(home: HomeSummary, stats: StatsSummary): Achievement[] {
  const h = stats.headline
  const chapter = highestChapterTouched(home)
  const accuracy = h.accuracy ?? 0
  const accuracyReady = h.commands_run >= 100
  const bossFloors = h.boss_floors?.value ?? 0
  const comebacks = h.comebacks?.value ?? 0

  const make = (
    id: AchievementImageId,
    title: string,
    desc: string,
    Icon: LucideIcon,
    color: string,
    points: number,
    current: number,
    target: number,
    unlockedOverride?: boolean,
  ): Achievement => ({
    id,
    title,
    desc,
    Icon,
    imageSrc: ACHIEVEMENT_IMAGES[id],
    color,
    points,
    current: Math.min(current, target),
    target,
    unlocked: unlockedOverride ?? current >= target,
  })

  // Achievement/reward moments render in the gold accent (--warning) so they read
  // consistently as "earned" rather than borrowing the navigation blue or other state colours.
  const GOLD = 'hsl(var(--warning))'

  return [
    make(
      'first-clear',
      'First Clean Run',
      'Clear your first Arcane Spire level',
      Swords,
      GOLD,
      10,
      h.levels_completed,
      1,
    ),
    make(
      'level-adept',
      'Pathfinder',
      'Clear 10 Arcane Spire levels',
      Swords,
      GOLD,
      15,
      h.levels_completed,
      10,
    ),
    make(
      'level-veteran',
      'Tower Archivist',
      'Clear 25 Arcane Spire levels',
      Medal,
      GOLD,
      20,
      h.levels_completed,
      25,
    ),
    make(
      'level-champion',
      'Chapter Champion',
      'Clear 50 Arcane Spire levels',
      Crown,
      GOLD,
      30,
      h.levels_completed,
      50,
    ),
    make('streak-spark', 'Daily Spark', 'Reach a 3-day streak', Flame, GOLD, 10, home.streak.longest, 3),
    make('weeklong-flame', 'Weeklong Flame', 'Reach a 7-day streak', Flame, GOLD, 20, home.streak.longest, 7),
    make('fortnight-blaze', 'Fortnight Blaze', 'Reach a 14-day streak', Flame, GOLD, 35, home.streak.longest, 14),
    make('perfectionist', 'Perfect Committer', 'Earn 5 perfect clears', Star, GOLD, 20, h.perfect_clears, 5),
    make('star-collector', 'Star Collector', 'Earn 25 perfect clears', Star, GOLD, 25, home.perfect_clears, 25),
    make(
      'boss-slayer',
      'Hard Tier Breaker',
      'Clear a Hard Arcane Spire tier',
      Swords,
      GOLD,
      15,
      bossFloors,
      1,
    ),
    make(
      'boss-reaper',
      'Hard Tier Hunter',
      'Clear 5 Hard Arcane Spire tiers',
      Swords,
      GOLD,
      30,
      bossFloors,
      5,
    ),
    make('comeback-kid', 'Recovery Artist', 'Turn 3 retries into wins', Sparkles, GOLD, 15, comebacks, 3),
    make('command-cadet', 'Command Cadet', 'Run 100 git commands', TerminalSquare, GOLD, 10, h.commands_run, 100),
    make('command-captain', 'Command Captain', 'Run 1,000 git commands', TerminalSquare, GOLD, 25, h.commands_run, 1000),
    make('coin-hoarder', 'Vault Keeper', 'Hold 500 GitCoins', Coins, GOLD, 20, h.gitcoins, 500),
    make(
      'sharpshooter',
      'Precision Operator',
      '90% accuracy over 100+ commands',
      Crosshair,
      GOLD,
      30,
      Math.round(accuracy),
      90,
      accuracyReady && accuracy >= 90,
    ),
    make('story-climber', 'Story Climber', 'Reach the third chapter', Castle, GOLD, 20, chapter, 3),
    make('story-sentinel', 'Story Sentinel', 'Reach the fifth chapter', Castle, GOLD, 35, chapter, 5),
    make(
      'arcane-spire-master',
      'Arcane Spire Master',
      'Master the Arcane Spire curriculum',
      Crown,
      GOLD,
      50,
      home.completed_stories?.includes('arcane-spire') ||
        home.completed_story_slug === 'arcane-spire'
        ? 1
        : 0,
      1,
    ),
  ]
}
