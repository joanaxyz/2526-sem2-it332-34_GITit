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

  return [
    make('first-clear', 'First Clean Run', 'Clear your first level', Swords, 'hsl(var(--success))', 10, home.counts.completed, 1),
    make('level-adept', 'Pathfinder', 'Clear 10 story levels', Swords, 'rgb(var(--theme-spark-rgb))', 15, home.counts.completed, 10),
    make('level-veteran', 'Tower Archivist', 'Clear 25 story levels', Medal, 'hsl(var(--primary))', 20, home.counts.completed, 25),
    make('level-champion', 'Chapter Champion', 'Clear 50 story levels', Crown, 'hsl(var(--warning))', 30, home.counts.completed, 50),
    make('streak-spark', 'Daily Spark', 'Reach a 3-day streak', Flame, 'hsl(var(--warning))', 10, home.streak.longest, 3),
    make('weeklong-flame', 'Weeklong Flame', 'Reach a 7-day streak', Flame, 'hsl(var(--warning))', 20, home.streak.longest, 7),
    make('fortnight-blaze', 'Fortnight Blaze', 'Reach a 14-day streak', Flame, 'rgb(var(--theme-challenge-rgb))', 35, home.streak.longest, 14),
    make('perfectionist', 'Perfect Committer', 'Earn 5 perfect clears', Star, 'hsl(var(--warning))', 20, h.perfect_clears, 5),
    make('star-collector', 'Star Collector', 'Earn 25 perfect clears', Star, 'hsl(var(--warning))', 25, home.perfect_clears, 25),
    make('boss-slayer', 'Trial Breaker', 'Win a hard challenge', Swords, 'rgb(var(--theme-challenge-rgb))', 15, bossFloors, 1),
    make('boss-reaper', 'Hard Trial Hunter', 'Win 5 hard challenges', Swords, 'rgb(var(--theme-challenge-rgb))', 30, bossFloors, 5),
    make('comeback-kid', 'Recovery Artist', 'Turn 3 retries into wins', Sparkles, 'rgb(var(--theme-challenge-rgb))', 15, comebacks, 3),
    make('command-cadet', 'Command Cadet', 'Run 100 git commands', TerminalSquare, 'rgb(var(--theme-spark-rgb))', 10, h.commands_run, 100),
    make('command-captain', 'Command Captain', 'Run 1,000 git commands', TerminalSquare, 'hsl(var(--accent))', 25, h.commands_run, 1000),
    make('coin-hoarder', 'Vault Keeper', 'Hold 500 GitCoins', Coins, 'rgb(var(--theme-challenge-rgb))', 20, h.gitcoins, 500),
    make(
      'sharpshooter',
      'Precision Operator',
      '90% accuracy over 100+ commands',
      Crosshair,
      'hsl(var(--success))',
      30,
      Math.round(accuracy),
      90,
      accuracyReady && accuracy >= 90,
    ),
    make('story-climber', 'Story Climber', 'Reach the third chapter', Castle, 'hsl(var(--primary))', 20, chapter, 3),
    make('story-sentinel', 'Story Sentinel', 'Reach the fifth chapter', Castle, 'rgb(var(--theme-challenge-rgb))', 35, chapter, 5),
    make(
      'arcane-spire-master',
      'Arcane Spire Master',
      'Complete the free foundations story',
      Crown,
      'hsl(var(--warning))',
      50,
      home.completed_stories?.includes('arcane-spire') || home.completed_story_slug === 'arcane-spire' ? 1 : 0,
      1,
    ),
  ]
}

/**
 * The badge surfaced in the hero banner's "Latest Achievement" card: the
 * highest-value badge currently unlocked (no unlock timestamps exist, so
 * "rarest earned" stands in for recency).
 */
export function latestAchievement(achievements: Achievement[]): Achievement | null {
  const unlocked = achievements.filter((a) => a.unlocked)
  if (unlocked.length === 0) return null
  return unlocked.reduce((best, a) => (a.points >= best.points ? a : best))
}
