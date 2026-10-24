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

import { RANK_TIERS } from '@/shared/progress/rank'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { ACHIEVEMENT_IMAGES, type AchievementImageId } from '@/features/home/utils/achievementImages'

/**
 * Client-derived achievement ledger. There is no achievements table in the
 * backend (yet) - every badge below is computed deterministically from the
 * home + stats summaries, so the set stays consistent across reloads.
 * `points` are cosmetic gamerscore-style stars, NOT GitCoins.
 *
 * Levels and chapters are not gated, so nothing here rewards reaching a
 * chapter or playing on consecutive days: badges count what was cleared and
 * how well, never where or when.
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

/** Each Arcane Spire module closes with one Challenge Gate. */
const CHALLENGE_GATE_COUNT = 4

function rankThreshold(name: string): number {
  const tier = RANK_TIERS.find((candidate) => candidate.name === name)
  if (!tier) throw new Error(`Unknown rank tier: ${name}`)
  return tier.minScore
}

export function deriveAchievements(home: HomeSummary, stats: StatsSummary): Achievement[] {
  const h = stats.headline
  const accuracy = h.accuracy ?? 0
  const accuracyReady = h.commands_run >= 100
  const hardTierClears = h.hard_tier_clears?.value ?? 0
  const comebacks = h.comebacks?.value ?? 0
  const mastery = Math.floor(home.mastery)

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

  // `levels_completed` counts cleared tiers (Easy, Medium and Hard are one each).
  return [
    make('first-clear', 'First Clean Run', 'Clear your first Arcane Spire tier', Swords, GOLD, 10, h.levels_completed, 1),
    make('level-adept', 'Pathfinder', 'Clear 10 Arcane Spire tiers', Swords, GOLD, 15, h.levels_completed, 10),
    make('level-veteran', 'Tower Archivist', 'Clear 30 Arcane Spire tiers', Medal, GOLD, 20, h.levels_completed, 30),
    make('level-champion', 'Spire Champion', 'Clear 50 Arcane Spire tiers', Crown, GOLD, 30, h.levels_completed, 50),
    make('hard-tier-breaker', 'Hard Tier Breaker', 'Clear a Hard tier', Swords, GOLD, 15, hardTierClears, 1),
    make('hard-tier-hunter', 'Hard Tier Hunter', 'Clear 5 Hard tiers', Swords, GOLD, 30, hardTierClears, 5),
    make('gate-breaker', 'Gatebreaker', 'Clear a Challenge Gate trial', Castle, GOLD, 20, h.gate_trial_clears, 1),
    make(
      'gate-warden',
      'Warden of the Gates',
      'Clear the Hard trial of every Challenge Gate',
      Castle,
      GOLD,
      40,
      h.hard_gate_trial_clears,
      CHALLENGE_GATE_COUNT,
    ),
    make('perfectionist', 'Perfect Committer', 'Earn 5 perfect clears', Star, GOLD, 20, h.perfect_clears, 5),
    make('star-collector', 'Star Collector', 'Earn 25 perfect clears', Star, GOLD, 25, h.perfect_clears, 25),
    make('rank-glyph-weaver', 'Glyph Weaver', 'Reach the Glyph Weaver rank', Flame, GOLD, 15, mastery, rankThreshold('Glyph Weaver')),
    make('rank-arcane-adept', 'Arcane Adept', 'Reach the Arcane Adept rank', Flame, GOLD, 25, mastery, rankThreshold('Arcane Adept')),
    make('rank-archon', 'Archon', 'Reach the Archon rank', Flame, GOLD, 40, mastery, rankThreshold('Archon')),
    make('comeback-kid', 'Recovery Artist', 'Turn 3 retries into wins', Sparkles, GOLD, 15, comebacks, 3),
    make('command-cadet', 'Command Cadet', 'Run 100 git commands', TerminalSquare, GOLD, 10, h.commands_run, 100),
    make('command-captain', 'Command Captain', 'Run 1,000 git commands', TerminalSquare, GOLD, 25, h.commands_run, 1000),
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
    make('coin-hoarder', 'Vault Keeper', 'Earn 1,000 GitCoins from tiers, gates and chests', Coins, GOLD, 20, h.gitcoins_earned, 1000),
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
