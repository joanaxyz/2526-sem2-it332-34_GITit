import { Castle, DoorOpen, Flag, RefreshCcw, Sparkles, Target, Trophy, XCircle } from 'lucide-react'
import type { CSSProperties } from 'react'

import type { AdventureRun } from '@/features/command-adventures/types'
import { CompletionModal, type CompletionStat } from '@/shared/level/components/completion/CompletionModal'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

// The single outcome surface shown when an adventure run ends. It reuses the
// shared CompletionModal so adventures and challenges celebrate the same way;
// the level navigator is challenge-only, so it is simply omitted here, while the
// per-command mastery breakdown is the adventure-specific extra section.
export function AdventureOutcomeModal({
  open,
  run,
  onRestart,
  onBackToTower,
  onClose,
}: {
  open: boolean
  run: AdventureRun
  onRestart: () => void
  onBackToTower?: () => void
  onClose: () => void
}) {
  const { session_score, pass_bar, total_achievable, commands_mastered, total_commands, passed, commands } =
    run.mastery
  const isReplay = run.mode === 'replay'
  const isFailed = !isReplay && !passed

  const headline = isReplay ? 'Replay complete' : passed ? 'Adventure passed' : 'Adventure ended'
  const message = isReplay
    ? 'Free play complete. This run is just a replay and doesn’t change your saved progress.'
    : passed
      ? 'You cleared the pass bar and unlocked this storey’s Challenge. Replay any time to sharpen your commands.'
      : 'This run ended before clearing the pass bar. Try again to grow your command mastery and unlock the Challenge.'

  const playAgainLabel = isReplay || passed ? 'Play again' : 'Try again'

  // Scoring only applies to counted (primary) runs; replays are uncounted, so
  // they recap mastery without the session-score framing.
  const stats: CompletionStat[] = isReplay
    ? [
        {
          label: 'Commands mastered',
          numerator: commands_mastered,
          denominator: total_commands,
          helper: 'Commands at full strength',
          icon: Trophy,
        },
      ]
    : [
        {
          label: 'Session score',
          numerator: session_score,
          denominator: total_achievable,
          helper: 'Points earned this run',
          icon: Target,
        },
        {
          label: 'Pass bar',
          numerator: pass_bar,
          helper: 'Points needed to pass',
          icon: Flag,
        },
        {
          label: 'Commands mastered',
          numerator: commands_mastered,
          denominator: total_commands,
          helper: 'Commands at full strength',
          icon: Trophy,
        },
      ]

  const badges = isReplay ? (
    <Badge variant="secondary" className="completion-badge" style={{ animationDelay: '60ms' } as CSSProperties}>
      <RefreshCcw className="size-3.5" />
      Free play
    </Badge>
  ) : passed ? (
    <Badge variant="default" className="completion-badge" style={{ animationDelay: '60ms' } as CSSProperties}>
      <DoorOpen className="size-3.5" />
      Challenge unlocked
    </Badge>
  ) : null

  const actions = (
    <>
      {onBackToTower ? (
        <Button type="button" variant="ghost" onClick={onBackToTower}>
          <Castle data-icon="inline-start" />
          Back to Tower
        </Button>
      ) : null}
      <Button type="button" onClick={onRestart}>
        <RefreshCcw data-icon="inline-start" />
        {playAgainLabel}
      </Button>
    </>
  )

  return (
    <CompletionModal
      open={open}
      onClose={onClose}
      title={`${headline} — ${run.command_adventure.title}`}
      tone={isFailed ? 'failure' : 'success'}
      icon={isFailed ? XCircle : Sparkles}
      badges={badges}
      headline={headline}
      message={message}
      stats={stats}
      actions={actions}
    >
      <div className="mt-5 overflow-hidden rounded-xl border border-border/50">
        <div className="flex items-center gap-1.5 border-b border-border/50 bg-card/50 px-3 py-2 font-mono text-[0.6rem] uppercase tracking-[0.16em] text-muted-foreground">
          <Trophy className="size-3" />
          Command mastery
        </div>
        <ul className="divide-y divide-border/40">
          {commands.map((command) => {
            const state = command.mastered ? 'mastered' : command.introduced ? 'progress' : 'untried'
            return (
              <li key={command.slug} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
                <span className="min-w-0 flex-1 truncate text-left font-medium text-foreground">{command.title}</span>
                <span className="shrink-0 font-mono text-xs text-muted-foreground">
                  {command.strength}/{command.mastered_bar}
                </span>
                <span
                  className={cn(
                    'shrink-0 rounded-full px-2 py-0.5 text-[0.65rem] font-semibold',
                    state === 'mastered' && 'bg-emerald-400/15 text-emerald-300',
                    state === 'progress' && 'bg-amber-400/15 text-amber-300',
                    state === 'untried' && 'bg-border/40 text-muted-foreground',
                  )}
                >
                  {state === 'mastered' ? 'Mastered' : state === 'progress' ? 'In progress' : 'Untried'}
                </span>
              </li>
            )
          })}
        </ul>
      </div>
    </CompletionModal>
  )
}
