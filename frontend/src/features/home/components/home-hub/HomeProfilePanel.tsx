import { Check, Lock, Star, Swords } from 'lucide-react'

import { HomeProfileCompanionStatus } from '@/features/home/components/home-hub/HomeCompanionStatus'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { RankBadge } from '@/features/home/components/HomeRankBadge'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { RANK_TIERS, deriveRank } from '@/shared/progress/rank'

type HomeProfilePanelProps = {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  companion: CompanionPresentation
}

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

/**
 * Who you are playing as, then the ladder you are climbing.
 *
 * These were two tabs behind a switch, which hid half the answer at all times
 * and only existed because both halves had to fit one fixed-height card. The
 * category is a column of open sections now, so they simply stack — and the
 * facts each one used to repeat (the mastery meter, the two clear counts) are
 * stated once, by whichever section owns them.
 */
export function HomeProfilePanel({
  home,
  stats,
  playerName,
  companion,
}: HomeProfilePanelProps) {
  const rank = deriveRank(home)
  const starsCollected = Math.max(stats.headline.perfect_clears, home.perfect_clears)
  const levelsCleared = stats.headline.levels_completed || home.counts.completed
  const companionPortrait = companion.status === 'ready'
    ? companion.definition.sprites.portrait?.src ?? companion.definition.sprites.idle?.src ?? ''
    : ''

  return (
    <aside className="home-profile-panel">
      <div className="home-profile-view">
        <div className="home-profile-portrait">
          {companion.status === 'ready' ? (
            <img src={companionPortrait} alt="" />
          ) : (
            <HomeProfileCompanionStatus companion={companion} />
          )}
        </div>
        <div className="home-profile-rank" data-onboarding="profile-rank">
          <RankBadge tier={rank.tier} className="home-rank-badge--profile" />
          <div>
            <span>Rank {rank.tier.numeral}</span>
            <div className="ref-meter" aria-label={`${rank.progressPct}% toward the next rank`}>
              <span style={{ width: `${rank.progressPct}%` }} />
            </div>
            <em>
              {rank.nextTier
                ? `${formatNumber(rank.ratingInTier)} / ${formatNumber(rank.ratingForNext)} mastery`
                : 'Max rank'}
            </em>
          </div>
        </div>
        <div className="home-profile-name">
          <strong>
            {playerName || (companion.status === 'ready' ? companion.definition.label : 'Adventurer')}
          </strong>
          <span>{rank.title}</span>
        </div>
        <div className="home-profile-currencies" data-onboarding="profile-currencies">
          <div>
            <Star className="is-lit" aria-hidden="true" />
            <strong>{formatNumber(starsCollected)}</strong>
            <span>Perfect Clears</span>
          </div>
          <div>
            <Swords aria-hidden="true" />
            <strong>{formatNumber(levelsCleared)}</strong>
            <span>Levels Cleared</span>
          </div>
        </div>
      </div>

      <div className="home-rank-view" data-onboarding="profile-ladder">
        <header className="ref-panel-head">
          Rank ladder <em>every tier, cleared and still locked</em>
        </header>
        {/* The current tier's crest, rating and meter live in the crest above;
            this is only the ladder it sits on. */}
        <div className="home-rank-list">
          {[...RANK_TIERS].reverse().map((tier) => {
            const state = tier.rank === rank.tier.rank
              ? 'current'
              : tier.rank < rank.tier.rank ? 'cleared' : 'locked'
            return (
              <div className={state === 'current' ? 'is-active' : ''} key={tier.name}>
                <RankBadge tier={tier} className="home-rank-badge--list" />
                <span>{tier.name}</span>
                {state === 'locked' ? <Lock aria-hidden="true" /> : null}
                {state === 'cleared' ? <Check aria-hidden="true" /> : null}
              </div>
            )
          })}
        </div>
        {/* Levels cleared and perfect clears are absent on purpose: the two
            counts above already state them. */}
        <div className="home-profile-stats">
          <div><span>Day Streak</span><strong>{formatNumber(home.streak.current)}</strong></div>
          <div><span>Commands Run</span><strong>{formatNumber(stats.headline.commands_run)}</strong></div>
        </div>
      </div>
    </aside>
  )
}
