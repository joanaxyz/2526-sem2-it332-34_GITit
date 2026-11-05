import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Infinity as InfinityIcon, Trophy } from 'lucide-react'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { leaderboardApi, type Leaderboard, type LeaderboardCategory } from '@/features/leaderboard/api/leaderboardApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { COMPANIONS } from '@/shared/cosmetics/companions/registry'
import { storyPath } from '@/shared/navigation/routes'
import { rankForXp } from '@/shared/progress/rank'

const CATEGORIES: ReadonlyArray<{
  id: LeaderboardCategory
  label: string
  unit: string
  heading: string
  icon: string
}> = [
  { id: 'xp', label: 'XP', unit: 'XP', heading: 'Total XP', icon: 'xp-crystal' },
  { id: 'perfect_clears', label: 'Perfect Clears', unit: 'clears', heading: 'Perfect clears', icon: 'perfect-clear-star' },
  { id: 'gates', label: 'Challenge Gates', unit: 'trials', heading: 'Trials cleared', icon: 'challenge-swords' },
]

type Category = (typeof CATEGORIES)[number]
type Entry = Leaderboard['entries'][number]

function categoryFromParam(value: string | null) {
  return CATEGORIES.find((category) => category.id === value) ?? CATEGORIES[0]
}

function CategoryIcon({ category, className = '' }: { category: Category; className?: string }) {
  return <img className={`leaderboard-icon ${className}`} src={`/leaderboard/${category.icon}.webp`} alt="" />
}

function LearnerAvatar({ entry }: { entry: Entry }) {
  const companion = entry.companion_slug && Object.hasOwn(COMPANIONS, entry.companion_slug)
    ? COMPANIONS[entry.companion_slug]
    : undefined
  const source = companion?.sprites.avatar?.src ?? companion?.sprites.portrait?.src
  const [failedSource, setFailedSource] = useState<string | null>(null)
  const initials = Array.from(entry.username.trim()).slice(0, 2).join('').toUpperCase() || '?'

  return (
    <span className="leaderboard-avatar" aria-hidden="true">
      {source && source !== failedSource ? (
        <img src={source} alt="" onError={() => setFailedSource(source)} />
      ) : (
        <span className="leaderboard-initials">{initials}</span>
      )}
    </span>
  )
}

function LearnerName({ entry, category }: { entry: Entry; category: Category }) {
  const tier = category.id === 'xp' ? rankForXp(entry.value).tier : null
  return (
    <span className="leaderboard-name">
      <span className="leaderboard-name-line">
        <strong title={entry.username}>{entry.username}</strong>
        {entry.is_you ? <span className="leaderboard-you-badge">You</span> : null}
      </span>
      {tier ? <small>Rank {tier.numeral} · {tier.name}</small> : null}
    </span>
  )
}

function Score({ entry, category }: { entry: Pick<Entry, 'value'>; category: Category }) {
  return (
    <span className="leaderboard-value">
      <CategoryIcon category={category} />
      <span>{entry.value.toLocaleString()} <small>{category.unit}</small></span>
    </span>
  )
}

function Champions({ entries, category }: { entries: Entry[]; category: Category }) {
  // A shared rank earns the same treatment. Only distinct places form a raised podium.
  const hasTies = new Set(entries.map((entry) => entry.rank)).size !== entries.length
  const classicPodium = entries.length === 3 && !hasTies
  const frameForRank: Record<number, string> = { 1: 'gold', 2: 'silver', 3: 'bronze' }

  return (
    <ol className={`leaderboard-podium${classicPodium ? ' is-classic' : ''}${hasTies ? ' has-ties' : ''}`} aria-label="Leading adventurers">
      {entries.map((entry) => (
        <li
          className={`leaderboard-champion place-${entry.rank}${entry.is_you ? ' is-you' : ''}`}
          key={entry.username}
          value={entry.rank}
        >
          <div className="leaderboard-champion-portrait">
            <LearnerAvatar entry={entry} />
            {frameForRank[entry.rank] ? (
              <img className="leaderboard-portrait-frame" src={`/leaderboard/frame-${frameForRank[entry.rank]}.webp`} alt="" />
            ) : null}
            <span className={frameForRank[entry.rank] ? 'sr-only' : 'leaderboard-medal'}>Place {entry.rank}</span>
          </div>
          <LearnerName entry={entry} category={category} />
          <Score entry={entry} category={category} />
        </li>
      ))}
    </ol>
  )
}

function YourPlace({ category, rank, value, hidden }: Leaderboard['you'] & { category: Category }) {
  return (
    <footer className="leaderboard-you">
      <div className="leaderboard-you-place">
        <Trophy aria-hidden="true" />
        {hidden ? (
          <p>You are hidden from the leaderboard. <Link to="/settings">Change this in Settings</Link></p>
        ) : rank === null ? (
          <p>You are not on this board yet. <span>Every adventure is a step up.</span></p>
        ) : (
          <p>Your rank <strong>#{rank.toLocaleString()}</strong><span className="leaderboard-you-score">{value.toLocaleString()} {category.unit}</span></p>
        )}
      </div>
      {!hidden ? <Link className="leaderboard-journey" to={storyPath()}>Continue your journey <ArrowRight aria-hidden="true" /></Link> : null}
    </footer>
  )
}

export function LeaderboardPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const category = categoryFromParam(searchParams.get('category'))
  const board = useQuery({
    queryKey: queryKeys.leaderboard(category.id),
    queryFn: () => leaderboardApi.get(category.id),
  })

  return (
    <section className="leaderboard-page" aria-labelledby="leaderboard-title">
      <header className="leaderboard-head">
        <div>
          <h1 id="leaderboard-title">Leaderboard</h1>
          <p>All-time standings across the Arcane Spire.</p>
        </div>
        <span className="leaderboard-period"><InfinityIcon aria-hidden="true" /> All-time</span>
      </header>

      <div className="leaderboard-tabs" role="group" aria-label="Leaderboard category">
        {CATEGORIES.map((option) => (
          <button
            type="button"
            aria-pressed={option.id === category.id}
            className={option.id === category.id ? 'is-active' : ''}
            key={option.id}
            onClick={() => setSearchParams((previous) => {
              const next = new URLSearchParams(previous)
              next.set('category', option.id)
              return next
            }, { replace: true })}
          >
            <CategoryIcon category={option} />
            <span>{option.label}</span>
          </button>
        ))}
      </div>

      {board.isPending ? (
        <div className="leaderboard-loading" role="status">
          <span className="sr-only">Loading leaderboard</span>
          <div className="leaderboard-loading-podium" aria-hidden="true"><i /><i /><i /></div>
          {Array.from({ length: 5 }, (_, index) => <i key={index} aria-hidden="true" />)}
        </div>
      ) : board.isError ? (
        <div className="leaderboard-error">
          <ErrorState title="Leaderboard unavailable" description={board.error.message} />
          <button type="button" onClick={() => void board.refetch()}>Try again</button>
        </div>
      ) : (
        <>
          {board.data.entries.length === 0 ? (
            <div className="leaderboard-empty">
              <Trophy aria-hidden="true" />
              <h2>The next chapter starts with you.</h2>
              <p>No one is on this board yet.</p>
              <p>Complete adventures to earn your place in the Spire.</p>
            </div>
          ) : (
            <>
              <Champions entries={board.data.entries.slice(0, 3)} category={category} />
              {board.data.entries.length > 3 ? (
                <div className="leaderboard-standings">
                  <div className="leaderboard-list-head" aria-hidden="true"><span>Rank</span><span>Adventurer</span><span>{category.heading}</span></div>
                  <ol className="leaderboard-list" aria-label="More adventurers" start={board.data.entries[3].rank}>
                    {board.data.entries.slice(3).map((entry) => (
                      <li className={`leaderboard-row${entry.is_you ? ' is-you' : ''}`} key={entry.username} value={entry.rank}>
                        <span className="leaderboard-rank"><span className="sr-only">Place </span>{entry.rank}</span>
                        <LearnerAvatar entry={entry} />
                        <LearnerName entry={entry} category={category} />
                        <Score entry={entry} category={category} />
                      </li>
                    ))}
                  </ol>
                </div>
              ) : null}
            </>
          )}
          <YourPlace category={category} {...board.data.you} />
        </>
      )}
    </section>
  )
}
