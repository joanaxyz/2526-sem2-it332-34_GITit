import { type CSSProperties, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Lock, Star } from 'lucide-react'

import { deriveAchievements } from '@/features/home/utils/achievements'
import type { HomeSummary } from '@/features/home/types'
import type { GitSkillMastery, StatsSummary, TrendPoint } from '@/features/stats/types'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'
import { storyPath } from '@/shared/navigation/routes'

type AchievementFilter = 'all' | 'unlocked' | 'locked'

type ActivityCell = {
  key: string
  date: string
  value: number
}

const ACHIEVEMENT_FILTERS: Array<{ value: AchievementFilter; label: string }> = [
  { value: 'all', label: 'All' },
  { value: 'unlocked', label: 'Unlocked' },
  { value: 'locked', label: 'Locked' },
]

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

function formatPercent(value: number | null | undefined) {
  return typeof value === 'number' ? `${Math.round(value)}%` : '--'
}

function formatDecimal(value: number | null | undefined, digits = 2) {
  return typeof value === 'number' ? value.toFixed(digits) : '--'
}

function dayLabel(iso: string) {
  if (!iso) return ''
  return new Date(`${iso}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function average(values: number[]) {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function buildActivityCells(points: TrendPoint[]): ActivityCell[] {
  const recent = points.slice(-14)
  const padCount = Math.max(0, 14 - recent.length)
  const padded: ActivityCell[] = Array.from({ length: padCount }, (_, index) => ({
    key: `empty-${index}`,
    date: '',
    value: 0,
  }))

  return [
    ...padded,
    ...recent.map((point) => ({
      key: point.date,
      date: point.date,
      value: point.commands_run + point.levels_completed * 4,
    })),
  ]
}

function SkillProfileBars({ rows }: { rows: GitSkillMastery[] }) {
  return (
    <div className="home-overview-command-list">
      {rows.map((row) => (
        <div className="home-overview-command-row" key={row.key} title={row.hint}>
          <GitCommandIcon command={row.command} className="home-overview-command-glyph" />
          <span>
            <strong>{row.label}</strong>
            <small>{row.hint}</small>
          </span>
          <div className="home-overview-command-meter" aria-label={`${row.label}: ${formatPercent(row.value)}`}>
            <span style={{ width: `${Math.max(0, Math.min(100, row.value ?? 0))}%` }} />
          </div>
          <strong>{formatPercent(row.value)}</strong>
        </div>
      ))}
    </div>
  )
}

function ActivityHeatmap({ cells }: { cells: ActivityCell[] }) {
  const max = Math.max(...cells.map((cell) => cell.value), 1)

  return (
    <div className="home-overview-activity" role="img" aria-label="Activity over the last 14 days">
      <div className="home-overview-weekdays" aria-hidden="true">
        {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => (
          <span key={`${day}-${index}`}>{day}</span>
        ))}
      </div>
      <div className="home-overview-heatmap">
        {cells.map((cell) => {
          const level = cell.value <= 0 ? 0 : Math.max(1, Math.ceil((cell.value / max) * 4))
          return (
            <span
              data-level={level}
              key={cell.key}
              title={cell.date ? `${dayLabel(cell.date)}: ${formatNumber(cell.value)} activity` : 'No data'}
            />
          )
        })}
      </div>
      <div className="home-overview-heatmap-scale" aria-hidden="true">
        <span>Less</span>
        <i data-level="1" />
        <i data-level="2" />
        <i data-level="3" />
        <i data-level="4" />
        <span>More</span>
      </div>
    </div>
  )
}

export function HomeStatsView({
  home,
  stats,
}: {
  home: HomeSummary
  stats: StatsSummary
}) {
  const [achievementFilter, setAchievementFilter] = useState<AchievementFilter>('all')
  const achievements = useMemo(() => deriveAchievements(home, stats), [home, stats])
  const activityCells = useMemo(() => buildActivityCells(stats.activity_trend), [stats.activity_trend])

  const unlocked = achievements.filter((achievement) => achievement.unlocked)
  const earnedPoints = unlocked.reduce((sum, achievement) => sum + achievement.points, 0)
  const totalPoints = achievements.reduce((sum, achievement) => sum + achievement.points, 0)
  const visibleAchievements = achievements
    .filter((achievement) => {
      if (achievementFilter === 'unlocked') return achievement.unlocked
      if (achievementFilter === 'locked') return !achievement.unlocked
      return true
    })
    .slice(0, 8)

  const skillValues = stats.skill_profile
    .map((axis) => axis.value)
    .filter((value): value is number => typeof value === 'number')
  const overallMastery = clampPercent(average(skillValues))
  const masteryStars = Math.min(3, Math.ceil(overallMastery / 34))
  const levelsCompleted = stats.headline.levels_completed || home.counts.completed
  // Finish rate is the only honest ratio the summary carries; there is no
  // "total levels in the game" here, so never fabricate a denominator.
  const trackProgress = clampPercent(stats.headline.finish_rate.value ?? 0)
  const accuracyReady = stats.headline.commands_run >= 100

  return (
    <section className="home-overview-grid" aria-label="Player overview">
      <header className="home-overview-continue">
        <div>
          <span>Recommended next step</span>
          <h2>Continue your Git journey</h2>
          <p>Return to the story map and pick up from the next available level.</p>
        </div>
        <Link className="home-overview-continue-action" to={storyPath()}>
          Continue story
          <ArrowRight aria-hidden="true" />
        </Link>
      </header>
      <section className="ref-panel home-overview-stats-panel" aria-label="Stats overview">
        <div className="home-overview-master-row">
          <div>
            <header className="ref-panel-head">Git Skill Mastery</header>
            <SkillProfileBars rows={stats.skill_profile} />
          </div>

          <aside className="home-overview-mastery-orb" aria-label={`Overall mastery ${overallMastery}%`}>
            <div className="home-overview-compass" aria-hidden="true">
              <span />
            </div>
            <span>Overall Mastery</span>
            <strong>{overallMastery}%</strong>
            <small>Proficiency</small>
            <div className="home-overview-rating-stars" aria-label={`${masteryStars} of 3 proficiency stars`}>
              {Array.from({ length: 3 }, (_, index) => (
                <i className={index < masteryStars ? 'is-lit' : ''} key={index} />
              ))}
            </div>
          </aside>
        </div>

        <div className="home-overview-stat-subgrid">
          <section className="home-overview-stat-block">
            <header className="ref-panel-head">14-Day Activity</header>
            <ActivityHeatmap cells={activityCells} />
          </section>

          <section className="home-overview-stat-block home-overview-story-block">
            <header className="ref-panel-head">Story Progress</header>
            <div className="home-overview-story-body">
              <div className="home-overview-story-sigil" aria-hidden="true">
                <span />
              </div>
              <dl>
                <div>
                  <dt>Levels Cleared</dt>
                  <dd>{formatNumber(levelsCompleted)}</dd>
                </div>
                <div>
                  <dt>Perfect Clears</dt>
                  <dd>{formatNumber(Math.max(stats.headline.perfect_clears, home.perfect_clears))}</dd>
                </div>
                <div>
                  <dt>Hard Trials Won</dt>
                  <dd>{formatNumber(stats.headline.boss_floors?.value)}</dd>
                </div>
              </dl>
            </div>
            <div className="ref-meter" aria-label={`Finish rate ${trackProgress}%`}>
              <span style={{ width: `${trackProgress}%` }} />
            </div>
          </section>
        </div>

        <div className="home-overview-kpi-row">
          <div>
            <span className="home-overview-mini-sigil is-accuracy" aria-hidden="true" />
            <strong>{formatPercent(home.kpis.scr.value)}</strong>
            <span>Clear rate</span>
            <small>
              {formatNumber(home.kpis.scr.numerator)} / {formatNumber(home.kpis.scr.denominator)} runs
            </small>
          </div>
          <div>
            <span className="home-overview-mini-sigil is-finish" aria-hidden="true" />
            <strong>{formatPercent(home.kpis.hlcr.value)}</strong>
            <span>Hard clear rate</span>
            <small>
              {formatNumber(home.kpis.hlcr.numerator)} / {formatNumber(home.kpis.hlcr.denominator)} hard runs
            </small>
          </div>
          <div>
            <span className="home-overview-mini-sigil is-streak" aria-hidden="true" />
            <strong>{formatDecimal(home.kpis.arc.value)}</strong>
            <span>Avg retries</span>
            <small>per cleared run</small>
          </div>
          <div>
            <span className="home-overview-mini-sigil is-commands" aria-hidden="true" />
            <strong>{accuracyReady ? formatPercent(stats.headline.accuracy) : '--'}</strong>
            <span>Accuracy</span>
            <small>{accuracyReady ? `${formatNumber(stats.headline.commands_run)} commands` : 'After 100 commands'}</small>
          </div>
        </div>
      </section>

      <section className="ref-panel home-overview-achievements-panel" aria-label="Achievement gallery">
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
          </div>
        </div>

        <div className="home-overview-achievement-tools" aria-label="Achievement filters">
          {ACHIEVEMENT_FILTERS.map((filter) => (
            <button
              type="button"
              className={achievementFilter === filter.value ? 'is-active' : ''}
              aria-pressed={achievementFilter === filter.value}
              key={filter.value}
              onClick={() => setAchievementFilter(filter.value)}
            >
              {filter.label}
            </button>
          ))}
        </div>

        <div className="home-overview-achievement-grid">
          {visibleAchievements.map((achievement) => {
            const pct = Math.round((achievement.current / Math.max(achievement.target, 1)) * 100)
            const style = {
              '--achievement-accent': achievement.unlocked ? achievement.color : 'rgba(117, 143, 159, 0.74)',
            } as CSSProperties

            return (
              <article
                className={`home-overview-achievement-card${achievement.unlocked ? ' is-unlocked' : ' is-locked'}`}
                key={achievement.id}
                style={style}
              >
                <span className="home-overview-achievement-medallion" aria-hidden="true">
                  {achievement.unlocked ? (
                    achievement.imageSrc ? (
                      <img src={achievement.imageSrc} alt="" />
                    ) : (
                      <achievement.Icon />
                    )
                  ) : (
                    <Lock />
                  )}
                </span>
                {achievement.unlocked ? (
                  <Star className="home-overview-achievement-earned" aria-hidden="true" />
                ) : null}
                <strong>{achievement.title}</strong>
                <span>{achievement.desc}</span>
                <div className="ref-meter" aria-label={`${achievement.title}: ${achievement.current} of ${achievement.target}`}>
                  <span style={{ width: `${Math.min(100, pct)}%` }} />
                </div>
                <small>
                  {achievement.current.toLocaleString()} / {achievement.target.toLocaleString()} - {achievement.points} pts
                </small>
              </article>
            )
          })}
        </div>
      </section>
    </section>
  )
}
