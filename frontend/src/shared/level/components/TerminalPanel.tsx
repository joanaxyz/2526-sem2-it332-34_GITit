import { useEffect, useMemo, useRef } from 'react'

import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

/** Lines after the most recent `clear`, like a real terminal's visible screen. */
function linesAfterClear(lines: TerminalLine[]) {
  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const line = lines[index]
    if (line.kind === 'input' && line.text.trim() === 'clear') return lines.slice(index + 1)
  }
  return lines
}

export function TerminalPanel({
  lines,
  prompt,
  cwd,
  disabled,
  runDisabled,
  processing,
  onCommand,
  title = 'Terminal',
  className,
}: {
  lines: TerminalLine[]
  prompt: string
  /** Terminal working directory relative to the project root (`''` at the root). */
  cwd?: string
  disabled?: boolean
  runDisabled?: boolean
  processing?: boolean
  onCommand: (command: string) => void
  title?: string
  className?: string
}) {
  const outputRef = useRef<HTMLDivElement>(null)
  const visibleLines = useMemo(() => linesAfterClear(lines), [lines])

  useEffect(() => {
    const container = outputRef.current
    if (!container) return
    container.scrollTop = container.scrollHeight
  }, [visibleLines])

  // Clicking anywhere in the scrollback focuses the prompt, like a real shell
  // (but never steal an in-progress text selection).
  function focusPrompt() {
    if (window.getSelection()?.toString()) return
    outputRef.current?.querySelector<HTMLInputElement>('[data-command-input]')?.focus()
  }

  return (
    <section
      aria-label={title}
      className={cn('terminal-panel', className)}
    >
      <div className="terminal-titlebar workspace-panel-header">
        <span className="panel-eyebrow">{title}</span>
      </div>

      {/* The prompt is the last line of the stream, not a separate bar. */}
      <div
        className="terminal-output app-scrollbar"
        ref={outputRef}
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
        onClick={focusPrompt}
      >
        {visibleLines.map((line) => (
          <div
            key={line.id}
            className={cn('terminal-line', `terminal-line--${line.kind}`)}
          >
            {line.kind === 'input' ? (
              <span className="terminal-prompt" aria-hidden="true">
                <span>{prompt}</span>
                <small>$ </small>
              </span>
            ) : null}
            {line.text}
          </div>
        ))}
        <CommandInput
          prompt={prompt}
          cwd={cwd}
          disabled={disabled}
          runDisabled={runDisabled}
          processing={processing}
          onSubmit={onCommand}
        />
      </div>
    </section>
  )
}
