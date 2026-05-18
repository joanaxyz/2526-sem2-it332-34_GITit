import type { TerminalLine } from '@/features/practice/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

export function TerminalPanel({
  lines,
  disabled,
  onCommand,
}: {
  lines: TerminalLine[]
  disabled?: boolean
  onCommand: (command: string) => void
}) {
  return (
    <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-black/40">
      <div className="border-b border-border px-4 py-3 font-mono text-xs text-muted-foreground">Terminal · simulated Git only</div>
      <div className="min-h-0 flex-1 overflow-auto p-4 font-mono text-sm leading-7">
        {lines.map((line) => (
          <div
            key={line.id}
            className={cn(
              line.kind === 'input' && 'text-foreground',
              line.kind === 'output' && 'text-muted-foreground',
              line.kind === 'system' && 'text-accent',
              line.kind === 'warning' && 'text-amber-300',
              line.kind === 'success' && 'text-primary',
            )}
          >
            {line.kind === 'input' ? <span className="text-primary">student@git-it $ </span> : null}
            {line.text}
          </div>
        ))}
      </div>
      <CommandInput disabled={disabled} onSubmit={onCommand} />
    </section>
  )
}
