import { DoorClosed, DoorOpen, Sparkles } from 'lucide-react'

import type { AdventureRun } from '@/features/command-adventures/types'
import { cn } from '@/shared/utils/cn'

/**
 * Mastery meter for an adventure session: the running session score climbing
 * toward the pass bar that unlocks Challenge, with a gate marker at the bar and
 * a tally of commands mastered. Replaces the old linear per-problem walk —
 * under spaced repetition commands repeat, so a fixed node-per-problem track no
 * longer fits.
 */
export function AdventureProgressBar({ run, className }: { run: AdventureRun; className?: string }) {
  const { session_score, pass_bar, total_achievable, commands_mastered, total_commands, passed } = run.mastery
  const ceiling = Math.max(total_achievable, 1)
  const fillPct = Math.min(100, Math.round((session_score / ceiling) * 100))
  const gatePct = Math.min(100, Math.round((pass_bar / ceiling) * 100))
  const toUnlock = Math.max(pass_bar - session_score, 0)

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <div className="flex items-center justify-between text-[10px] font-semibold uppercase tracking-normal text-muted-foreground">
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
        aria-valuemax={ceiling}
        aria-valuenow={session_score}
        aria-label={`Session score ${session_score} of ${ceiling}; pass bar at ${pass_bar}`}
      >
        <span
          className={cn(
            'absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-primary to-accent transition-all',
            passed && 'shadow-[0_0_12px_rgba(0,180,216,0.55)]',
          )}
          style={{ width: `${fillPct}%` }}
        />
        <span
          aria-hidden="true"
          className="absolute -top-1 z-10 -translate-x-1/2"
          style={{ left: `${gatePct}%` }}
          title={passed ? 'Challenge unlocked' : `Reach ${pass_bar} pts to unlock Challenge`}
        >
          {passed ? (
            <DoorOpen className="size-4 text-accent drop-shadow-[0_0_4px_rgba(0,180,216,0.7)]" />
          ) : (
            <DoorClosed className="size-4 text-muted-foreground" />
          )}
        </span>
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="font-mono font-bold text-foreground">
          {session_score}
          <span className="font-sans font-normal text-muted-foreground"> / {total_achievable} pts</span>
        </span>
        {passed ? (
          <span className="inline-flex items-center gap-1 font-semibold text-accent">
            <Sparkles className="size-3.5" /> Challenge unlocked
          </span>
        ) : (
          <span className="text-muted-foreground">{toUnlock} to unlock</span>
        )}
      </div>
    </div>
  )
}
