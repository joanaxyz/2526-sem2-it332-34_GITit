import { useState } from 'react'
import { Check, Lock, Star, Trophy, User } from 'lucide-react'

import { HomeProfileCompanionStatus } from '@/features/home/components/home-hub/HomeCompanionStatus'
import type { CompanionPresentation } from '@/features/home/components/home-hub/companionPresentation'
import { RankBadge } from '@/features/home/components/HomeRankBadge'
import type { HomeSummary } from '@/features/home/types'
import type { StatsSummary } from '@/features/stats/types'
import { RANK_TIERS, deriveRank } from '@/shared/progress/rank'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'

type HomeProfilePanelProps = {
  home: HomeSummary
  stats: StatsSummary
  playerName: string
  gitcoins: number | null
  companion: CompanionPresentation
}

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

export function HomeProfilePanel({
  home,
  stats,
  playerName,
  gitcoins,
  companion,
}: HomeProfilePanelProps) {
  const [profileView, setProfileView] = useState<'profile' | 'rank'>('profile')
  const rank = deriveRank(home)
  const balance = gitcoins ?? stats.headline.gitcoins ?? 0
  const starsCollected = Math.max(stats.headline.perfect_clears, home.perfect_clears)
  const levelsCleared = stats.headline.levels_completed || home.counts.completed
  const companionPortrait = companion.status === 'ready'
    ? companion.definition.sprites.portrait?.src ?? companion.definition.sprites.idle?.src ?? ''
    : ''

  return (
    <aside className={`ref-panel home-profile-panel home-profile-panel--${profileView}`}>
      <div className="home-panel-switch" role="tablist" aria-label="Profile or rank ladder" data-onboarding="profile-switch">
        <button
          type="button"
          role="tab"
          className={profileView === 'profile' ? 'is-active' : ''}
          aria-selected={profileView === 'profile'}
          onClick={() => setProfileView('profile')}
        >
          <User aria-hidden="true" />
          Profile
        </button>
        <button
          type="button"
          role="tab"
          className={profileView === 'rank' ? 'is-active' : ''}
          aria-selected={profileView === 'rank'}
          onClick={() => setProfileView('rank')}
        >
          <Trophy aria-hidden="true" />
          Rank Ladder
        </button>
      </div>

      {profileView === 'profile' ? (
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
              <small>{rank.tier.name}</small>
              <div className="ref-meter" aria-label={`${rank.progressPct}% toward the next rank`}>
                <span style={{ width: `${rank.progressPct}%` }} />
              </div>
              <em>
                {rank.nextTier
                  ? `${formatNumber(rank.ratingInTier)} / ${formatNumber(rank.ratingForNext)} XP`
                  : 'Max rank'}
              </em>
            </div>
          </div>
          <div className="home-profile-name">
            <strong>
              {playerName || (companion.status === 'ready' ? companion.definition.label : 'Adventurer')}
            </strong>
            <span>{rank.tier.name}</span>
          </div>
          <div className="home-profile-currencies" data-onboarding="profile-currencies">
            <div>
              <GitCoinIcon />
              <strong>{formatNumber(balance)}</strong>
              <span>GitCoins</span>
            </div>
            <div>
              <Star className="is-lit" aria-hidden="true" />
              <strong>{formatNumber(starsCollected)}</strong>
              <span>Perfect Clears</span>
            </div>
          </div>
          <div className="home-profile-title">
            <RankBadge tier={rank.tier} className="home-rank-badge--title" />
            <span>Current Title</span>
            <strong>{rank.title}</strong>
          </div>
        </div>
      ) : (
        <div className="home-rank-view">
          <div className="home-rank-body">
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
            <div className="home-current-rank">
              <div className="home-current-rank-crest">
                <RankBadge tier={rank.tier} className="home-rank-badge--current" />
              </div>
              <span>{rank.tier.name}</span>
              <small>Your Rating</small>
              <strong>
                {formatNumber(rank.score)}{' '}
                <em>/ {formatNumber(rank.nextTier ? rank.nextTier.minScore : rank.score)}</em>
              </strong>
              <div className="ref-meter" aria-label={`${rank.progressPct}% toward the next rank`}>
                <span style={{ width: `${rank.progressPct}%` }} />
              </div>
            </div>
          </div>
          <div className="home-profile-stats">
            <header>Profile Stats</header>
            <div><span>Levels Cleared</span><strong>{formatNumber(levelsCleared)}</strong></div>
            <div><span>Perfect Clears</span><strong>{formatNumber(starsCollected)}</strong></div>
            <div><span>Day Streak</span><strong>{formatNumber(home.streak.current)}</strong></div>
            <div><span>Commands Run</span><strong>{formatNumber(stats.headline.commands_run)}</strong></div>
          </div>
        </div>
      )}
    </aside>
  )
}
