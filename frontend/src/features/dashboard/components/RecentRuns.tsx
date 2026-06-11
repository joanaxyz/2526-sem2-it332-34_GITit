import { ArrowRight, Swords } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { DashboardSummary } from '@/features/dashboard/types'
import { GamePanel } from '@/shared/components/GamePanel'

type RunAccent = { hex: string; rgb: string; tag: string }

/** Color-code a run by how heavy its retries were. */
function runAccent(retries: number): RunAccent {
  if (retries === 0) return { hex: '#34D399', rgb: '52, 211, 153', tag: 'CLEAN' }
  if (retries <= 2) return { hex: '#00F5D4', rgb: '0, 245, 212', tag: 'SOLID' }
  if (retries <= 4) return { hex: '#FBBF24', rgb: '251, 191, 36', tag: 'GRIND' }
  return { hex: '#F472B6', rgb: '244, 114, 182', tag: 'HEAVY' }
}

const OUTCOME_CHIPS: { key: keyof DashboardSummary['counts']; label: string; color: string }[] = [
  { key: 'started', label: 'Started', color: '#7DD3FC' },
  { key: 'completed', label: 'Completed', color: '#34D399' },
  { key: 'failed', label: 'Failed', color: '#FB7185' },
  { key: 'abandoned', label: 'Abandoned', color: '#94A3B8' },
  { key: 'review_started', label: 'Reviews', color: '#A78BFA' },
]

function OutcomeChips({ counts }: { counts: DashboardSummary['counts'] }) {
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
 * Match-history style list of recent runs, sourced from retry trends.
 * Falls back to outcome summary chips + an invitation when there are no runs.
 */
export function RecentRuns({ summary }: { summary: DashboardSummary }) {
  const runs = summary.retry_trends.slice(0, 8)

  return (
    <GamePanel className="flex flex-col p-5">
      <div className="relative z-[1] mb-3 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-mono text-[0.66rem] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
            Recent Runs
          </h3>
          <p className="mt-1 text-xs text-muted-foreground">Your latest quest attempts, color-coded by retries.</p>
        </div>
        <Link
          to="/stats"
          className="group inline-flex shrink-0 items-center gap-1 font-mono text-[0.64rem] font-semibold uppercase tracking-[0.1em] text-aurora-cyan/80 transition-colors hover:text-aurora-cyan"
        >
          Full profile
          <ArrowRight aria-hidden="true" className="size-3 transition-transform group-hover:translate-x-0.5" />
        </Link>
      </div>

      {runs.length > 0 ? (
        <ol className="relative z-[1] flex flex-col gap-1.5" aria-label="Recent quest runs">
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
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold leading-tight">{run.practice_title}</p>
                  <p className="mt-0.5 truncate font-mono text-[0.6rem] uppercase tracking-[0.08em] text-muted-foreground/65">
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
        <div className="relative z-[1] flex flex-col items-center gap-3 rounded-lg border border-dashed border-aurora-blue/20 px-6 py-8 text-center">
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
      <div className="relative z-[1] mt-4 border-t pt-3" style={{ borderColor: 'rgba(255,255,255,0.06)' }}>
        <OutcomeChips counts={summary.counts} />
      </div>
    </GamePanel>
  )
}
