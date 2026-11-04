import { type CSSProperties, useState } from 'react'
import { Lock } from 'lucide-react'

import type { Achievement } from '@/features/home/utils/achievements'

type AchievementFilter = 'all' | 'unlocked' | 'locked'

const ACHIEVEMENT_FILTERS: Array<{ value: AchievementFilter; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'unlocked', label: 'Unlocked' },
  { value: 'locked', label: 'Locked' },
]

const EMPTY_FILTER_COPY: Record<AchievementFilter, string> = {
  all: '',
  unlocked: 'Nothing unlocked yet. Clear your first tier to start the collection.',
  locked: 'Every achievement unlocked.',
}

function matchesFilter(achievement: Achievement, filter: AchievementFilter) {
  if (filter === 'unlocked') return achievement.unlocked
  if (filter === 'locked') return !achievement.unlocked
  return true
}

function AchievementBadge({ achievement }: { achievement: Achievement }) {
  const pct = Math.round((achievement.current / Math.max(achievement.target, 1)) * 100)
  const style = {
    '--achievement-accent': achievement.unlocked ? achievement.color : 'hsl(var(--warning) / 0.55)',
  } as CSSProperties

  return (
    <article
      className={`home-overview-achievement-card${achievement.unlocked ? ' is-unlocked' : ' is-locked'}`}
      style={style}
    >
      {/* Locked art stays visible, dimmed: the badge is what is being worked toward. */}
      <span className="home-overview-achievement-medallion" aria-hidden="true">
        {achievement.imageSrc ? <img src={achievement.imageSrc} alt="" /> : <achievement.Icon />}
        {achievement.unlocked ? null : (
          <i className="home-overview-achievement-lock"><Lock /></i>
        )}
      </span>
      <strong>{achievement.title}</strong>
      <span>{achievement.desc}</span>
      {achievement.unlocked ? (
        <small>Unlocked · {achievement.points} pts</small>
      ) : (
        <>
          <div className="ref-meter" aria-label={`${achievement.title}: ${achievement.current} of ${achievement.target}`}>
            <span style={{ width: `${Math.min(100, pct)}%` }} />
          </div>
          <small>
            {achievement.current.toLocaleString()} / {achievement.target.toLocaleString()} · {achievement.points} pts
          </small>
        </>
      )}
    </article>
  )
}

export function HomeAchievementGallery({ achievements }: { achievements: Achievement[] }) {
  const [filter, setFilter] = useState<AchievementFilter>('all')
  const unlocked = achievements.filter((achievement) => achievement.unlocked)
  const earnedPoints = unlocked.reduce((sum, achievement) => sum + achievement.points, 0)
  const totalPoints = achievements.reduce((sum, achievement) => sum + achievement.points, 0)
  const pointsPct = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0
  const groups = [...new Set(achievements.map((achievement) => achievement.group))].map((label) => {
    const members = achievements.filter((achievement) => achievement.group === label)
    return {
      label,
      earned: members.filter((achievement) => achievement.unlocked).length,
      total: members.length,
      // Every match is shown: a capped shelf would contradict the filter's count.
      visible: members.filter((achievement) => matchesFilter(achievement, filter)),
    }
  }).filter((group) => group.visible.length > 0)

  return (
    <section className="home-overview-achievements-panel" aria-label="Achievements" data-onboarding="overview-achievements">
      <div className="home-overview-achievements-head">
        <div className="home-overview-achievements-tally">
          <header className="ref-panel-head">Achievements</header>
          <p>
            <strong>{unlocked.length}</strong> / {achievements.length} unlocked
          </p>
        </div>
        <div className="home-overview-award-score">
          <strong>{earnedPoints}</strong>
          <span>/ {totalPoints} pts</span>
          <div className="ref-meter" aria-label={`${earnedPoints} of ${totalPoints} achievement points earned`}>
            <span style={{ width: `${pointsPct}%` }} />
          </div>
        </div>
      </div>

      <div className="home-overview-achievement-tools" aria-label="Achievement filters">
        {ACHIEVEMENT_FILTERS.map((option) => (
          <button
            type="button"
            className={filter === option.value ? 'is-active' : ''}
            aria-pressed={filter === option.value}
            key={option.value}
            onClick={() => setFilter(option.value)}
          >
            {option.label}{' '}
            <b>{achievements.filter((achievement) => matchesFilter(achievement, option.value)).length}</b>
          </button>
        ))}
      </div>

      {groups.length === 0 ? <p className="home-overview-achievement-empty">{EMPTY_FILTER_COPY[filter]}</p> : null}

      {groups.map((group) => (
        <section className="home-overview-achievement-set" aria-label={group.label} key={group.label}>
          <header className="home-overview-achievement-set-head">
            <h3>{group.label}</h3>
            <span>{group.earned} / {group.total}</span>
          </header>
          <div className="home-overview-achievement-grid">
            {group.visible.map((achievement) => (
              <AchievementBadge achievement={achievement} key={achievement.id} />
            ))}
          </div>
        </section>
      ))}
    </section>
  )
}
