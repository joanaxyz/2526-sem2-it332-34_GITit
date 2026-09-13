import { useState } from 'react'

import { MasteryRadar } from '@/shared/components/charts/MasteryRadar'
import { GitCommandIcon } from '@/shared/git/commandCatalog/commandIcons'

import type { HomeSkillProfileRow, HomeSkillsModel } from './homeStatsModel'

function formatPercent(value: number | null | undefined) {
  return typeof value === 'number' ? `${Math.round(value)}%` : '--'
}

/** The precise readout: every command, its summary, and its exact number. */
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

/**
 * One profile, two readings of it.
 *
 * Bars are the default because they carry every exact value in text; the dial
 * is the opt-in view for the question bars answer badly — whether the profile is
 * even or spiked. They switch rather than sit side by side, which is what lets
 * this band stand beside the achievement gallery instead of above it.
 */
export function HomeSkillsPanel({ skills }: { skills: HomeSkillsModel }) {
  // Whichever view is up, pointing at a command lights it: a row lights its own
  // glyph, a vertex lights its rim label and the dial's hub.
  const [activeKey, setActiveKey] = useState<string | null>(null)
  const [asShape, setAsShape] = useState(false)

  return (
    <section
      className="home-overview-stats-panel"
      aria-label="Git skills"
      data-onboarding="overview-skills"
    >
      <div className="home-overview-band-head">
        <header className="ref-panel-head">
          Command confidence <em>how reliably you reach for each one</em>
        </header>
        <div className="home-overview-segmented" role="group" aria-label="Skill profile view">
          <button
            aria-pressed={!asShape}
            className={asShape ? '' : 'is-active'}
            onClick={() => setAsShape(false)}
            type="button"
          >
            Bars
          </button>
          <button
            aria-pressed={asShape}
            className={asShape ? 'is-active' : ''}
            onClick={() => setAsShape(true)}
            type="button"
          >
            Radar
          </button>
        </div>
      </div>

      {asShape ? (
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
            label={`Mastery across ${skills.rows.length} git commands, overall ${skills.overallMastery}%. Switch to Bars for every value in text.`}
            onActiveKeyChange={setActiveKey}
            overall={skills.overallMastery}
          />
          <div className="home-overview-rating-stars" aria-label={`${skills.masteryStars} of 3 proficiency stars`}>
            {Array.from({ length: 3 }, (_, index) => (
              <i className={index < skills.masteryStars ? 'is-lit' : ''} key={index} />
            ))}
          </div>
          <small>Overall mastery across all {skills.rows.length} commands</small>
        </aside>
      ) : (
        <SkillProfileBars activeKey={activeKey} onHover={setActiveKey} rows={skills.rows} />
      )}
    </section>
  )
}
