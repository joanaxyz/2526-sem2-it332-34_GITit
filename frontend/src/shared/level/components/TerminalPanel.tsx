import { useEffect, useRef } from 'react'

import type { TerminalPrompt } from '@/shared/level/terminalPrompt'
import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

export function TerminalPanel({
  lines,
  prompt,
  disabled,
  runDisabled,
  processing,
  onCommand,
  title = 'Terminal',
  className,
}: {
  lines: TerminalLine[]
  prompt: TerminalPrompt
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
      <div className="terminal-titlebar">
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
        {lines.length === 0 ? (
          <div className="terminal-line terminal-line--hint">
            The repository is ready. Type a git command to begin.
          </div>
        ) : null}
        {lines.map((line) => (
          <div
            key={line.id}
            className={cn('terminal-line', `terminal-line--${line.kind}`)}
          >
            {line.kind === 'input' ? (
              <span className="terminal-prompt" aria-hidden="true">
                <span>{prompt.user}@{prompt.host}</span>
                <small>:</small>
                <b>{prompt.cwd}</b>
                <small>$ </small>
              </span>
            ) : null}
            {line.text}
          </div>
        ))}
        <CommandInput
          prompt={prompt}
          disabled={disabled}
          runDisabled={runDisabled}
          processing={processing}
          onSubmit={onCommand}
        />
      </div>
    </section>
  )
}
