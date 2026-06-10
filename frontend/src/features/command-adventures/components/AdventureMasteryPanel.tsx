import { Crown, Lock } from 'lucide-react'

import type { AdventureMasteryCommand, AdventureRun } from '@/features/command-adventures/types'
import { cn } from '@/shared/utils/cn'

/**
 * Per-command Leitner state for the session: each command shows filled "rune"
 * pips for its current mastery box out of the bar it must reach. Mastered
 * commands earn a crown; not-yet-introduced ones stay dimmed behind a lock.
 */
function MasteryPips({ command }: { command: AdventureMasteryCommand }) {
  return (
    <span
      className="flex items-center gap-0.5"
      aria-label={`${command.strength} of ${command.mastered_bar} mastery`}
    >
      {Array.from({ length: Math.max(command.mastered_bar, 1) }, (_, index) => (
        <span
          key={index}
          className={cn(
            'h-1.5 w-3 rounded-full transition-colors',
            index < command.strength ? 'bg-gradient-to-r from-primary to-accent' : 'bg-secondary',
            command.mastered && index < command.strength && 'shadow-[0_0_5px_rgba(0,180,216,0.55)]',
          )}
        />
      ))}
    </span>
  )
}

export function AdventureMasteryPanel({ run, className }: { run: AdventureRun; className?: string }) {
  const { commands } = run.mastery
  return (
    <section
      className={cn('rounded-lg border border-border bg-card/60 p-3', className)}
      aria-label="Command mastery"
    >
      <h2 className="mb-2 text-[10px] font-semibold uppercase tracking-normal text-muted-foreground">
        Command mastery
      </h2>
      <ul className="flex flex-col gap-2">
        {commands.map((command) => (
          <li key={command.slug} className="flex items-center justify-between gap-3">
            <span
              className={cn(
                'flex min-w-0 items-center gap-1.5 text-xs',
                !command.introduced && 'text-muted-foreground/60',
              )}
            >
              {command.mastered ? (
                <Crown className="size-3.5 shrink-0 text-accent" />
              ) : !command.introduced ? (
                <Lock className="size-3 shrink-0 text-muted-foreground/50" />
              ) : null}
              <span className="truncate">{command.title}</span>
            </span>
            <MasteryPips command={command} />
          </li>
        ))}
      </ul>
    </section>
  )
}
