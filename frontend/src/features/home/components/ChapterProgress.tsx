import { Castle } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { HomeSummary, RateMetric } from '@/features/home/types'
import { GamePanel } from '@/shared/components/GamePanel'
import { storyPath } from '@/shared/navigation/routes'

function MiniBar({ label, metric, color }: { label: string; metric: RateMetric; color: string }) {
  const hasData = metric.value !== null
  const pct = Math.max(0, Math.min(100, metric.value ?? 0))
  return (
    <div className="flex items-center gap-2">
      <span className="w-9 shrink-0 font-mono text-[11px] font-semibold uppercase tracking-[0.08em] text-muted-foreground/70">
        {label}
      </span>
      <div className="h-1.5 min-w-0 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
        {hasData && (
          <div
            className="h-full rounded-full"
            style={{
              width: '100%',
              background: `linear-gradient(90deg, ${color}88, ${color})`,
              boxShadow: `0 0 6px ${color}66`,
              transform: `scaleX(${pct / 100})`,
              transformOrigin: 'left center',
              transition: 'transform 1s cubic-bezier(0.16, 1, 0.3, 1)',
            }}
          />
        )}
      </div>
      <span
        className="w-8 shrink-0 text-right font-mono text-[11px] font-bold"
        style={{ color: hasData ? color : 'hsl(var(--foreground) / 0.3)' }}
      >
        {hasData ? `${Math.round(pct)}%` : '-'}
      </span>
    </div>
  )
}

/**
 * Per-chapter story record - glowing door motif per floor with scenario/hard
 * clear bars and retry micro-stats. The "Most Played" analog.
 */
export function ChapterProgress({ summary }: { summary: HomeSummary }) {
  const chapters = Object.entries(summary.chapter_kpis)
    .map(([chapter, kpis]) => ({ chapter: Number(chapter), kpis }))
    .filter(({ chapter }) => Number.isFinite(chapter))
    .sort((a, b) => a.chapter - b.chapter)

  return (
    <GamePanel className="flex flex-col p-5">
      <div className="relative z-[1] mb-3">
        <h3 className="font-mono text-[11px] font-semibold uppercase tracking-[0.2em] text-aurora-blue/80">
          Story Record
        </h3>
        <p className="mt-1 text-xs text-muted-foreground">Floor-by-floor performance.</p>
      </div>

      {chapters.length > 0 ? (
        <ol className="relative z-[1] flex flex-col gap-2.5" aria-label="Per-chapter performance">
          {chapters.map(({ chapter, kpis }, i) => (
            <li
              key={chapter}
              className="animate-fade-in-up flex items-center gap-3 rounded-lg border border-white/[0.05] bg-white/[0.02] p-2.5"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <span className="chapter-door-chip" aria-hidden="true">
                {chapter}
              </span>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-baseline justify-between gap-2">
                  <p className="text-xs font-bold tracking-tight">Chapter {chapter}</p>
                  <p className="font-mono text-[11px] text-muted-foreground/60">
                    clear {kpis.scr.value === null ? '-' : `${Math.round(kpis.scr.value)}%`} - ret{' '}
                    {kpis.arc.value === null ? '-' : `${kpis.arc.value.toFixed(1)}x`}
                  </p>
                </div>
                <div className="flex flex-col gap-1">
                  <MiniBar label="SCR" metric={kpis.scr} color="hsl(var(--primary))" />
                  <MiniBar label="HARD" metric={kpis.hlcr} color="rgb(var(--theme-challenge-rgb))" />
                </div>
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <div className="relative z-[1] flex flex-col items-center gap-3 rounded-lg border border-dashed border-aurora-blue/20 px-6 py-7 text-center">
          <span className="game-chip size-11">
            <Castle aria-hidden="true" className="size-5 text-aurora-cyan" />
          </span>
          <p className="text-sm font-semibold">No floors climbed yet</p>
          <p className="max-w-xs text-xs leading-5 text-muted-foreground">
            Each chapter you enter starts its own record of clears and retries.
          </p>
          <Link
            to={storyPath()}
            className="font-mono text-[11px] font-semibold uppercase tracking-[0.1em] text-aurora-cyan/80 transition-colors hover:text-aurora-cyan"
          >
            {'Continue the story ->'}
          </Link>
        </div>
      )}
    </GamePanel>
  )
}
