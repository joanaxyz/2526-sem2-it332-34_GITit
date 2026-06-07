import { useEffect, useRef } from 'react'

import type { TerminalLine } from '@/shared/practice/types'
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
    <section
      aria-label={title}
      className={cn('flex min-h-0 flex-col overflow-hidden rounded-lg border border-white/[0.08] bg-[#0d1117]', className)}
    >
      {/* macOS-style title bar */}
      <div className="relative flex shrink-0 items-center border-b border-white/[0.08] bg-[#1c1f26] px-3 py-2.5">
        <div className="flex items-center gap-1.5" aria-hidden="true">
          <span className="size-3 rounded-full bg-[#ff5f57]" />
          <span className="size-3 rounded-full bg-[#febc2e]" />
          <span className="size-3 rounded-full bg-[#28c840]" />
        </div>
        <span className="absolute left-1/2 -translate-x-1/2 font-mono text-[11px] text-muted-foreground/55">
          {title}
        </span>
      </div>

      {/* Terminal output */}
      <div className="min-h-0 flex-1 overflow-auto p-3 font-mono text-xs leading-6 app-scrollbar">
        {lines.map((line) => (
          <div
            key={line.id}
            className={cn(
              line.kind === 'input' && 'text-foreground',
              line.kind === 'output' && 'text-primary/80',
              line.kind === 'system' && 'text-accent',
              line.kind === 'warning' && 'text-accent',
              line.kind === 'success' && 'text-primary',
            )}
          >
            {line.kind === 'input' ? (
              <span aria-hidden="true">
                <span className="text-emerald-400">student@git-it</span>
                <span className="text-muted-foreground/55">:</span>
                <span className="text-primary">~</span>
                <span className="text-muted-foreground/55"> $ </span>
              </span>
            ) : null}
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
