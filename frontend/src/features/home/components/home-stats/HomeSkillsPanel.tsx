import { useState } from 'react'

import { MasteryRadar } from '@/shared/components/charts/MasteryRadar'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'

import type { HomeSkillProfileRow, HomeSkillsModel } from './homeStatsModel'

function formatPercent(value: number | null | undefined) {
  return typeof value === 'number' ? `${Math.round(value)}%` : '--'
}

/** The precise readout, and the radar's table-view twin: every value in text. */
function SkillProfileBars({
  rows,
  activeKey,
  onHover,
}: {
  rows: HomeSkillProfileRow[]
  activeKey: string | null
  onHover: (key: string | null) => void
}) {
  return (
    <div className="home-overview-command-list" onMouseLeave={() => onHover(null)}>
      {rows.map((row) => {
        const hasProgress = (row.value ?? 0) > 0
        return (
          <div
            className={`home-overview-command-row${hasProgress ? ' is-progressed' : ''}${row.key === activeKey ? ' is-active' : ''}`}
            key={row.key}
            onMouseEnter={() => onHover(row.key)}
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

export function HomeSkillsPanel({ skills }: { skills: HomeSkillsModel }) {
  // Hovering a row lights its point on the radar, so the shape and the numbers
  // read as one instrument rather than two views of the same list.
  const [activeKey, setActiveKey] = useState<string | null>(null)

  return (
    <section
      className="home-overview-stats-panel"
      aria-label="Git skills"
      data-onboarding="overview-skills"
    >
      <div className="home-overview-master-row">
        <div>
          <header className="ref-panel-head">Command confidence</header>
          <SkillProfileBars activeKey={activeKey} onHover={setActiveKey} rows={skills.rows} />
        </div>

        <aside className="home-overview-mastery-orb" aria-label={`Overall mastery ${skills.overallMastery}%`}>
          <MasteryRadar
            activeKey={activeKey}
            axes={skills.rows.map((row) => ({
              key: row.key,
              label: row.label,
              short: row.short,
              value: row.value,
              caption: row.hint,
            }))}
            label={`Mastery across ${skills.rows.length} git commands, overall ${skills.overallMastery}%. Every value is listed beside this shape.`}
          />
          <span>Overall mastery</span>
          <strong>{skills.overallMastery}%</strong>
          <small>Across all commands</small>
          <div className="home-overview-rating-stars" aria-label={`${skills.masteryStars} of 3 proficiency stars`}>
            {Array.from({ length: 3 }, (_, index) => (
              <i className={index < skills.masteryStars ? 'is-lit' : ''} key={index} />
            ))}
          </div>
        </aside>
      </div>
    </section>
  )
}
