import type { TerminalLine } from '@/features/practice/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

export function TerminalPanel({
  lines,
  disabled,
  onCommand,
  title = 'Terminal',
  className,
}: {
  lines: TerminalLine[]
  disabled?: boolean
  onCommand: (command: string) => void
  title?: string
  className?: string
}) {
  return (
    <section className={cn('flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-black/40', className)}>
      <div className="border-b border-border px-3 py-2 font-mono text-[11px] text-muted-foreground">{title}</div>
      <div className="min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-6">
        {lines.map((line) => (
          <div
            key={line.id}
            className={cn(
              line.kind === 'input' && 'text-foreground',
              line.kind === 'output' && 'text-muted-foreground',
              line.kind === 'system' && 'text-accent',
              line.kind === 'warning' && 'text-accent',
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
