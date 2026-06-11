import { Swords } from 'lucide-react'

import type { HomeSummary } from '@/features/home/types'

type RunAccent = { hex: string; rgb: string; tag: string }

/** Encode retry load inside the tower palette instead of a rainbow scale. */
function runAccent(retries: number): RunAccent {
  if (retries === 0) return { hex: '#00F5D4', rgb: '0, 245, 212', tag: 'CLEAN' }
  if (retries <= 2) return { hex: '#00B4D8', rgb: '0, 180, 216', tag: 'SOLID' }
  if (retries <= 4) return { hex: '#7DD3FC', rgb: '125, 211, 252', tag: 'GRIND' }
  return { hex: '#94A3B8', rgb: '148, 163, 184', tag: 'HEAVY' }
}

const OUTCOME_CHIPS: { key: keyof HomeSummary['counts']; label: string; color: string }[] = [
  { key: 'started', label: 'Started', color: '#7DD3FC' },
  { key: 'completed', label: 'Completed', color: '#00F5D4' },
  { key: 'failed', label: 'Failed', color: '#94A3B8' },
  { key: 'abandoned', label: 'Abandoned', color: '#94A3B8' },
  { key: 'review_started', label: 'Reviews', color: '#00B4D8' },
]

function OutcomeChips({ counts }: { counts: HomeSummary['counts'] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {OUTCOME_CHIPS.map(({ key, label, color }) => (
        <span
          key={key}
          className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-mono text-[0.62rem] font-semibold"
          style={{ border: `1px solid ${color}40`, background: `${color}10`, color }}
        >
          {counts[key]} <span className="font-medium uppercase tracking-[0.08em] opacity-80">{label}</span>
        </span>
      ))}
    </div>
  )
}

/**
 * Match-history style list of recent runs as an open hairline ledger.
 * Falls back to outcome summary chips + an invitation when there are no runs.
 */
export function RecentRuns({ summary }: { summary: HomeSummary }) {
  const runs = summary.retry_trends.slice(0, 8)

  return (
    <section className="flex flex-col" aria-label="Recent runs">
      <h3 className="text-[0.95rem] font-bold tracking-tight">Recent Runs</h3>

      {runs.length > 0 ? (
        <ol className="mt-2 flex flex-col" aria-label="Recent quest runs">
          {runs.map((run, i) => {
            const accent = runAccent(run.retries)
            return (
              <li
                key={`${run.practice_title}-${i}`}
                className="match-row animate-fade-in-up"
                style={{
                  ['--run-accent' as string]: accent.hex,
                  ['--run-accent-rgb' as string]: accent.rgb,
                  animationDelay: `${i * 45}ms`,
                }}
              >
                <span className="match-dot" aria-hidden="true" />
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold leading-tight">{run.practice_title}</p>
                  <p className="mt-0.5 truncate font-mono text-[0.6rem] uppercase tracking-[0.08em] text-muted-foreground/85">
                    {run.label}
                  </p>
                </div>
                <div className="flex items-center gap-3 font-mono text-[0.66rem]">
                  <span
                    className="hidden w-12 text-right font-bold tracking-[0.08em] sm:inline"
                    style={{ color: accent.hex, textShadow: `0 0 10px ${accent.hex}55` }}
                  >
                    {accent.tag}
                  </span>
                  <span className="w-12 text-right text-muted-foreground">
                    <span className="font-bold text-foreground/90">{run.attempts}</span> att
                  </span>
                  <span className="w-12 text-right text-muted-foreground">
                    <span className="font-bold" style={{ color: accent.hex }}>
                      {run.retries}
                    </span>{' '}
                    ret
                  </span>
                </div>
              </li>
            )
          })}
        </ol>
      ) : (
        <div className="mt-3 flex flex-col items-center gap-3 rounded-lg border border-dashed border-aurora-blue/20 px-6 py-8 text-center">
          <span className="game-chip size-11">
            <Swords aria-hidden="true" className="size-5 text-aurora-cyan" />
          </span>
          <p className="text-sm font-semibold">No runs on record yet</p>
          <p className="max-w-xs text-xs leading-5 text-muted-foreground">
            Enter the tower and clear your first quest — every attempt lands here as match history.
          </p>
        </div>
      )}

      {/* Outcome ledger — every session ever, by how it ended */}
      <div className="mt-4 pt-3">
        <OutcomeChips counts={summary.counts} />
      </div>
    </section>
  )
}
