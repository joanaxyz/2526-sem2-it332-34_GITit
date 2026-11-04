import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'

import { leaderboardApi, type LeaderboardCategory } from '@/features/leaderboard/api/leaderboardApi'
import { queryKeys } from '@/shared/api/queryKeys'
import { ErrorState } from '@/shared/components/ErrorState'
import { rankForXp } from '@/shared/progress/rank'

const CATEGORIES: ReadonlyArray<{ id: LeaderboardCategory; label: string; unit: string }> = [
  { id: 'xp', label: 'XP', unit: 'XP' },
  { id: 'perfect_clears', label: 'Perfect Clears', unit: 'clears' },
  { id: 'gates', label: 'Challenge Gates', unit: 'trials' },
]

function categoryFromParam(value: string | null) {
  return CATEGORIES.find((category) => category.id === value) ?? CATEGORIES[0]
}

function YourPlace({
  category,
  rank,
  value,
  hidden,
}: {
  category: (typeof CATEGORIES)[number]
  rank: number | null
  value: number
  hidden: boolean
}) {
  if (hidden) {
    return (
      <p className="leaderboard-you">
        You are hidden from the leaderboard. <Link to="/settings">Change this in Settings</Link>
      </p>
    )
  }
  if (rank === null) {
    return <p className="leaderboard-you">You are not on this board yet.</p>
  }
  return (
    <p className="leaderboard-you">
      Your rank <strong>#{rank}</strong> · {value.toLocaleString()} {category.unit}
    </p>
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
        <h1 id="leaderboard-title">Leaderboard</h1>
        <p>All-time standings across the Arcane Spire.</p>
      </header>

      <div className="leaderboard-tabs" role="group" aria-label="Leaderboard category">
        {CATEGORIES.map((option) => (
          <button
            type="button"
            aria-pressed={option.id === category.id}
            className={option.id === category.id ? 'is-active' : ''}
            key={option.id}
            onClick={() => setSearchParams({ category: option.id }, { replace: true })}
          >
            {option.label}
          </button>
        ))}
      </div>

      {board.isPending ? (
        <div className="leaderboard-loading" role="status">
          <span className="sr-only">Loading leaderboard</span>
          {Array.from({ length: 5 }, (_, index) => <i key={index} aria-hidden="true" />)}
        </div>
      ) : board.isError ? (
        <ErrorState title="Leaderboard unavailable" description={board.error.message} />
      ) : (
        <>
          {board.data.entries.length === 0 ? (
            <p className="leaderboard-empty">No one is on this board yet.</p>
          ) : (
            <ol className="leaderboard-list">
              {board.data.entries.map((entry) => {
                const tier = category.id === 'xp' ? rankForXp(entry.value).tier : null
                return (
                  <li className={`leaderboard-row${entry.is_you ? ' is-you' : ''}`} key={entry.username}>
                    <span className="leaderboard-rank">{entry.rank}</span>
                    <span className="leaderboard-name">
                      <strong>{entry.username}{entry.is_you ? ' (you)' : ''}</strong>
                      {tier ? <small>Rank {tier.numeral} · {tier.name}</small> : null}
                    </span>
                    <span className="leaderboard-value">
                      {entry.value.toLocaleString()} <small>{category.unit}</small>
                    </span>
                  </li>
                )
              })}
            </ol>
          )}
          {board.data.entries.some((entry) => entry.is_you) ? null : (
            <YourPlace category={category} {...board.data.you} />
          )}
        </>
      )}
    </section>
  )
}
