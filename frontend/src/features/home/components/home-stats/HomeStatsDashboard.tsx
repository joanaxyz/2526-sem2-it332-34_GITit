import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'

import type { HomeActivityCell, HomeSkillProfileRow, HomeStatsDashboardModel } from './homeStatsModel'

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

function SkillProfileBars({ rows }: { rows: HomeSkillProfileRow[] }) {
  return (
    <div className="home-overview-command-list">
      {rows.map((row) => {
        const hasProgress = (row.value ?? 0) > 0
        return (
          <div
            className={`home-overview-command-row${hasProgress ? ' is-progressed' : ''}`}
            key={row.key}
            title={row.hint}
          >
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
        )
      })}
    </div>
  )
}

function ActivityHeatmap({ cells }: { cells: HomeActivityCell[] }) {
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

export function HomeStatsDashboard({ dashboard }: { dashboard: HomeStatsDashboardModel }) {
  const { kpis, story } = dashboard

  return (
    <section className="ref-panel home-overview-stats-panel" aria-label="Stats overview">
      <div className="home-overview-master-row">
        <div>
          <header className="ref-panel-head">Git Skill Mastery</header>
          <SkillProfileBars rows={dashboard.skillRows} />
        </div>

        <aside className="home-overview-mastery-orb" aria-label={`Overall mastery ${dashboard.overallMastery}%`}>
          <div className="home-overview-compass" aria-hidden="true">
            <span />
          </div>
          <span>Overall Mastery</span>
          <strong>{dashboard.overallMastery}%</strong>
          <small>Proficiency</small>
          <div className="home-overview-rating-stars" aria-label={`${dashboard.masteryStars} of 3 proficiency stars`}>
            {Array.from({ length: 3 }, (_, index) => (
              <i className={index < dashboard.masteryStars ? 'is-lit' : ''} key={index} />
            ))}
          </div>
        </aside>
      </div>

      <div className="home-overview-stat-subgrid">
        <section className="home-overview-stat-block">
          <header className="ref-panel-head">14-Day Activity</header>
          <ActivityHeatmap cells={dashboard.activityCells} />
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
                <dd>{formatNumber(story.levelsCompleted)}</dd>
              </div>
              <div>
                <dt>Perfect Clears</dt>
                <dd>{formatNumber(story.perfectClears)}</dd>
              </div>
              <div>
                <dt>Hard Trials Won</dt>
                <dd>{formatNumber(story.hardTrialsWon)}</dd>
              </div>
            </dl>
          </div>
          <div className="ref-meter" aria-label={`Finish rate ${story.trackProgress}%`}>
            <span style={{ width: `${story.trackProgress}%` }} />
          </div>
        </section>
      </div>

      <div className="home-overview-kpi-row">
        <div>
          <span className="home-overview-mini-sigil is-accuracy" aria-hidden="true" />
          <strong>{formatPercent(kpis.clearRate.value)}</strong>
          <span>Clear rate</span>
          <small>{formatNumber(kpis.clearRate.numerator)} / {formatNumber(kpis.clearRate.denominator)} runs</small>
        </div>
        <div>
          <span className="home-overview-mini-sigil is-finish" aria-hidden="true" />
          <strong>{formatPercent(kpis.hardClearRate.value)}</strong>
          <span>Hard clear rate</span>
          <small>{formatNumber(kpis.hardClearRate.numerator)} / {formatNumber(kpis.hardClearRate.denominator)} hard runs</small>
        </div>
        <div>
          <span className="home-overview-mini-sigil is-streak" aria-hidden="true" />
          <strong>{formatDecimal(kpis.averageRetries.value)}</strong>
          <span>Avg retries</span>
          <small>per cleared run</small>
        </div>
        <div>
          <span className="home-overview-mini-sigil is-commands" aria-hidden="true" />
          <strong>{kpis.accuracyReady ? formatPercent(kpis.accuracy) : '--'}</strong>
          <span>Accuracy</span>
          <small>{kpis.accuracyReady ? `${formatNumber(kpis.commandsRun)} commands` : 'After 100 commands'}</small>
        </div>
      </div>
    </section>
  )
}
