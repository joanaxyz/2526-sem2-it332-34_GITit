import { useEffect, useId, useRef, useState } from 'react'
import { ChevronRight, Crown, Lock, ScrollText } from 'lucide-react'

import type { AdventureMasteryCommand, AdventureRun } from '@/features/adventures/types'
import { cn } from '@/shared/utils/cn'

/**
 * Per-command Leitner state for the current adventure, surfaced as a quiet
 * toggle pinned to the battle stage's top-right corner instead of a panel in
 * the scenario column. Collapsed, it is just a glass chip echoing the HP
 * meter's vocabulary with a mastered/total tally; expanded, it reveals a
 * transparent, scrollable list of every command in this adventure.
 *
 * The command set is the adventure's own (the run payload is scoped to the
 * adventure in primary play), so this never leaks mastery from other chapters.
 */
export function AdventureMasteryOverlay({ run }: { run: AdventureRun }) {
  const { commands, commands_mastered, total_commands } = run.mastery
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const panelId = useId()

  // Dismiss on Escape or a click outside, the way a popover behaves; the chip
  // itself stays the only persistent affordance over the arena.
  useEffect(() => {
    if (!open) return undefined
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }
    function onPointerDown(event: PointerEvent) {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [open])

  if (!commands.length) return null

  return (
    <div ref={containerRef} className="flex flex-col items-end gap-1.5">
      <button
        type="button"
        aria-expanded={open}
        aria-controls={panelId}
        aria-label={`Command mastery: ${commands_mastered} of ${total_commands} mastered`}
        onClick={() => setOpen((value) => !value)}
        className={cn(
          'flex items-center gap-1.5 rounded-md border px-2 py-1 text-[11px] font-semibold backdrop-blur-sm',
          'transition-colors motion-reduce:transition-none',
          open
            ? 'border-primary/45 bg-background/80 text-primary'
            : 'border-primary/25 bg-background/70 text-foreground/80 hover:border-primary/40 hover:text-primary',
        )}
      >
        <Crown className="size-3.5 shrink-0 text-accent" />
        <span className="font-mono tabular-nums">
          {commands_mastered}
          <span className="font-sans font-normal text-muted-foreground">/{total_commands}</span>
        </span>
        <ChevronRight
          className={cn(
            'size-3 shrink-0 text-muted-foreground transition-transform motion-reduce:transition-none',
            open ? 'rotate-90' : 'rotate-0',
          )}
          aria-hidden
        />
      </button>

      <div
        id={panelId}
        aria-hidden={!open}
        className={cn(
          'w-52 max-w-[min(14rem,60vw)] max-h-[11rem] origin-top-right overflow-y-auto rounded-md',
          'border border-primary/15 bg-background/80 p-2 shadow-lg backdrop-blur-md app-scrollbar',
          'transition duration-150 ease-out motion-reduce:transition-none',
          open
            ? 'pointer-events-auto translate-y-0 scale-100 opacity-100'
            : 'pointer-events-none -translate-y-1 scale-95 opacity-0',
        )}
        // Capped to fit inside the shortest stage (clamp min 14rem) so a long
        // command list scrolls within the panel instead of overrunning the arena.
      >
        <div className="mb-1.5 flex items-center gap-1.5 px-0.5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
          <ScrollText className="size-3 text-primary" />
          Command mastery
        </div>
        <ul className="flex flex-col gap-1.5">
          {commands.map((command) => (
            <li key={command.slug} className="flex items-center justify-between gap-2">
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
                ) : (
                  <span className="size-3 shrink-0" aria-hidden />
                )}
                <span className="truncate">{command.title}</span>
              </span>
              <MasteryPips command={command} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

/**
 * Filled "rune" pips for a command's current Leitner box out of the bar it must
 * reach; mastered commands glow. Mirrors the meter the scenario-column panel
 * used so the visual reads identically in its new home.
 */
function MasteryPips({ command }: { command: AdventureMasteryCommand }) {
  return (
    <span
      className="flex shrink-0 items-center gap-0.5"
      aria-label={`${command.strength} of ${command.mastered_bar} mastery`}
    >
      {Array.from({ length: Math.max(command.mastered_bar, 1) }, (_, index) => (
        <span
          key={index}
          className={cn(
            'h-1.5 w-3 rounded-full transition-colors motion-reduce:transition-none',
            index < command.strength ? 'bg-gradient-to-r from-primary to-accent' : 'bg-secondary',
            command.mastered && index < command.strength && 'shadow-[0_0_5px_rgba(var(--theme-accent-rgb),0.55)]',
          )}
        />
      ))}
    </span>
  )
}
