import { useEffect, useRef } from 'react'

import type { TerminalLine } from '@/features/practice/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

export function TerminalPanel({
  lines,
  disabled,
  runDisabled,
  processing,
  onCommand,
  title = 'Terminal',
  className,
}: {
  lines: TerminalLine[]
  disabled?: boolean
  runDisabled?: boolean
  processing?: boolean
  onCommand: (command: string) => void
  title?: string
  className?: string
}) {
  const outputRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const container = outputRef.current
    if (!container) return
    container.scrollTop = container.scrollHeight
  }, [lines])

  return (
    <section className={cn('flex min-h-0 flex-col overflow-hidden rounded-lg border border-border bg-black/40', className)}>
      <div className="border-b border-border px-3 py-2 font-mono text-[11px] text-muted-foreground">{title}</div>
      <div ref={outputRef} className="min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-6 app-scrollbar">
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
      <CommandInput
        disabled={disabled}
        runDisabled={runDisabled}
        processing={processing}
        onSubmit={onCommand}
      />
    </section>
  )
}
