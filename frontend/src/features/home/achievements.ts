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

import { highestStoreyTouched } from '@/features/home/rank'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'

/**
 * Client-derived achievement ledger. There is no achievements table in the
 * backend (yet) - every badge below is computed deterministically from the
 * home + stats summaries, so the set stays consistent across reloads.
 * `points` are cosmetic gamerscore-style stars, NOT GitCoins (coins only
 * ever come from storey chests).
 */
export type Achievement = {
  id: string
  title: string
  desc: string
  Icon: LucideIcon
  color: string
  points: number
  current: number
  target: number
  unlocked: boolean
}

export function deriveAchievements(home: HomeSummary, stats: StatsSummary): Achievement[] {
  const h = stats.headline
  const storey = highestStoreyTouched(home)
  const accuracy = h.accuracy ?? 0
  const accuracyReady = h.commands_run >= 100

  const make = (
    id: string,
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
    color,
    points,
    current: Math.min(current, target),
    target,
    unlocked: unlockedOverride ?? current >= target,
  })

  return [
    make('first-clear', 'First Clear', 'Complete your first level', Swords, '#34D399', 10, home.counts.completed, 1),
    make('level-adept', 'Level Adept', 'Complete 10 levels', Swords, '#7DD3FC', 15, home.counts.completed, 10),
    make('level-veteran', 'Level Veteran', 'Complete 25 levels', Medal, '#00F5D4', 20, home.counts.completed, 25),
    make('level-champion', 'Level Champion', 'Complete 50 levels', Crown, '#FBBF24', 30, home.counts.completed, 50),
    make('streak-spark', 'Streak Spark', 'Reach a 3-day streak', Flame, '#FB923C', 10, home.streak.longest, 3),
    make('weeklong-flame', 'Weeklong Flame', 'Reach a 7-day streak', Flame, '#FB923C', 20, home.streak.longest, 7),
    make('fortnight-blaze', 'Fortnight Blaze', 'Reach a 14-day streak', Flame, '#F472B6', 35, home.streak.longest, 14),
    make('perfectionist', 'Perfectionist', 'Earn 5 perfect clears', Star, '#FBBF24', 20, h.perfect_clears, 5),
    make('star-collector', 'Star Collector', 'Earn 25 first-attempt stars', Star, '#FBBF24', 25, home.first_attempt_stars, 25),
    make('boss-slayer', 'Boss Slayer', 'Beat a hard challenge', Swords, '#A78BFA', 15, h.boss_floors.value, 1),
    make('boss-reaper', 'Boss Reaper', 'Beat 5 hard challenges', Swords, '#A78BFA', 30, h.boss_floors.value, 5),
    make('comeback-kid', 'Comeback Kid', 'Turn 3 retries into wins', Sparkles, '#F472B6', 15, h.comebacks.value, 3),
    make('command-cadet', 'Command Cadet', 'Run 100 git commands', TerminalSquare, '#7DD3FC', 10, h.commands_run, 100),
    make('command-captain', 'Command Captain', 'Run 1,000 git commands', TerminalSquare, '#00B4D8', 25, h.commands_run, 1000),
    make('coin-hoarder', 'Coin Hoarder', 'Hold 500 GitCoins', Coins, '#A78BFA', 20, h.gitcoins, 500),
    make(
      'sharpshooter',
      'Sharpshooter',
      '90% accuracy over 100+ commands',
      Crosshair,
      '#34D399',
      30,
      Math.round(accuracy),
      90,
      accuracyReady && accuracy >= 90,
    ),
    make('tower-climber', 'Tower Climber', 'Reach the third storey', Castle, '#00F5D4', 20, storey, 3),
    make('tower-sentinel', 'Tower Sentinel', 'Reach the fifth storey', Castle, '#A78BFA', 35, storey, 5),
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
