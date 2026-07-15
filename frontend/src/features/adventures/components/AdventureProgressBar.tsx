import { RefreshCcw, Sparkles, Trophy } from 'lucide-react'

import type { AdventureRun } from '@/features/adventures/types'
import { cn } from '@/shared/utils/cn'

/**
 * Mastery meter for an adventure session: monsters cleared vs total, with a
 * victory indicator once the adventure is passed.
 */
export function AdventureProgressBar({
  run,
  variant = 'panel',
  currentWave,
  totalWaves,
  className,
}: {
  run: AdventureRun
  /** `battle` = the slim single-row strip under the battle stage's ground line. */
  variant?: 'panel' | 'battle'
  currentWave?: number
  totalWaves?: number
  className?: string
}) {
  const { commands_mastered, total_commands, total_achievable, passed } = run.mastery
  const isReplay = run.replay
  const monsters = Math.max(total_commands, 1)
  const clearedPct = Math.min(100, Math.round((commands_mastered / monsters) * 100))
  const waveCurrent = Math.max(1, currentWave ?? run.current_wave ?? 1)
  const waveTotal = Math.max(waveCurrent, totalWaves ?? run.total_waves ?? waveCurrent)
  const clearedWaves =
    run.status === 'completed' ? waveTotal : Math.max(0, Math.min(waveTotal, waveCurrent - 1))
  const wavePct = Math.min(100, Math.round((clearedWaves / waveTotal) * 100))

  if (variant === 'battle') {
    return (
      <div
        className={cn(
          'flex items-center gap-2 px-1',
          className,
        )}
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={waveTotal}
        aria-valuenow={clearedWaves}
        aria-valuetext={`Wave ${waveCurrent} of ${waveTotal}, ${clearedWaves} cleared`}
        aria-label={`Wave ${waveCurrent} of ${waveTotal}`}
      >
        <span className="text-[11px] font-semibold uppercase tracking-normal text-muted-foreground">Wave</span>
        <div className="relative h-2 min-w-0 flex-1 overflow-hidden rounded-[2px] bg-secondary/80">
          <span
            className="absolute inset-y-0 left-0 rounded-[2px] bg-gradient-to-r from-primary to-accent transition-all"
            style={{ width: `${wavePct}%` }}
          />
          {Array.from({ length: waveTotal - 1 }, (_, i) => (
            <span
              key={i}
              aria-hidden
              className="absolute inset-y-0 w-px bg-foreground/30"
              style={{ left: `${((i + 1) / waveTotal) * 100}%` }}
            />
          ))}
        </div>
        <span className="shrink-0 font-mono text-[11px] font-bold text-foreground/90">
          {waveCurrent}
          <span className="font-sans font-normal text-muted-foreground">/{waveTotal}</span>
        </span>
      </div>
    )
  }

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-normal text-muted-foreground">
        <span>Mastery</span>
        <span className="inline-flex items-center gap-1.5 normal-case">
          <span className="font-mono font-bold text-foreground">
            {commands_mastered}/{total_commands}
          </span>
          <span>mastered</span>
        </span>
      </div>
      <div
        className="relative h-2.5 rounded-full bg-secondary"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={Math.max(total_achievable, 1)}
        aria-valuenow={commands_mastered}
        aria-label={`${commands_mastered} of ${total_commands} commands mastered`}
      >
        <span
          className={cn(
            'absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-primary to-accent transition-all',
            passed && 'shadow-[0_0_12px_rgba(var(--theme-accent-rgb),0.55)]',
          )}
          style={{ width: `${clearedPct}%` }}
        />
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="inline-flex items-center gap-1 font-mono text-xs text-muted-foreground">
          <Trophy className="size-3" />
          {commands_mastered}/{total_commands}
        </span>
        {isReplay ? (
          <span className="inline-flex items-center gap-1 font-semibold text-accent">
            <RefreshCcw className="size-3.5" /> Replay
          </span>
        ) : passed ? (
          <span className="inline-flex items-center gap-1 font-semibold text-accent">
            <Sparkles className="size-3.5" /> Challenge unlocked
          </span>
        ) : null}
      </div>
    </div>
  )
}
