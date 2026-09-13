import { type CSSProperties, useState } from 'react'
import { Lock, Star } from 'lucide-react'

import type { Achievement } from '@/features/home/utils/achievements'

type AchievementFilter = 'all' | 'unlocked' | 'locked'

const ACHIEVEMENT_FILTERS: Array<{ value: AchievementFilter; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'unlocked', label: 'Unlocked' },
  { value: 'locked', label: 'Locked' },
]

function matchesFilter(achievement: Achievement, filter: AchievementFilter) {
  if (filter === 'unlocked') return achievement.unlocked
  if (filter === 'locked') return !achievement.unlocked
  return true
}

export function HomeAchievementGallery({ achievements }: { achievements: Achievement[] }) {
  const [filter, setFilter] = useState<AchievementFilter>('all')
  const unlocked = achievements.filter((achievement) => achievement.unlocked)
  const earnedPoints = unlocked.reduce((sum, achievement) => sum + achievement.points, 0)
  const totalPoints = achievements.reduce((sum, achievement) => sum + achievement.points, 0)
  // Every match is shown. The gallery used to stop at eight cards, so a filter
  // could report sixteen unlocked and then display half of them.
  const visibleAchievements = achievements.filter((achievement) => matchesFilter(achievement, filter))
  const pointsPct = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0

  return (
    <section className="home-overview-achievements-panel" aria-label="Achievement gallery" data-onboarding="overview-achievements">
      <div className="home-overview-achievements-head">
        <div>
          <header className="ref-panel-head">Achievement Gallery</header>
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

      <div className="home-overview-achievement-grid">
        {visibleAchievements.map((achievement) => {
          const pct = Math.round((achievement.current / Math.max(achievement.target, 1)) * 100)
          const style = {
            '--achievement-accent': achievement.unlocked ? achievement.color : 'hsl(var(--warning) / 0.55)',
          } as CSSProperties

          return (
            <article
              className={`home-overview-achievement-card${achievement.unlocked ? ' is-unlocked' : ' is-locked'}`}
              key={achievement.id}
              style={style}
            >
              <span className="home-overview-achievement-medallion" aria-hidden="true">
                {achievement.unlocked ? (
                  achievement.imageSrc ? <img src={achievement.imageSrc} alt="" /> : <achievement.Icon />
                ) : (
                  <Lock />
                )}
              </span>
              {achievement.unlocked ? <Star className="home-overview-achievement-earned" aria-hidden="true" /> : null}
              <strong>{achievement.title}</strong>
              <span>{achievement.desc}</span>
              <div className="ref-meter" aria-label={`${achievement.title}: ${achievement.current} of ${achievement.target}`}>
                <span style={{ width: `${Math.min(100, pct)}%` }} />
              </div>
              {/* Tight on purpose: this column is what squeezes the title when
                  the gallery runs five across on a wide screen. */}
              <small>
                {achievement.current.toLocaleString()}/{achievement.target.toLocaleString()} · {achievement.points} pts
              </small>
            </article>
          )
        })}
      </div>
    </section>
  )
}
