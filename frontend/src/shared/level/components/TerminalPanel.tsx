import { useEffect, useMemo, useRef } from 'react'
import type { ReactNode } from 'react'

import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'

/** How close (px) to the end of the scrollback still counts as "at the bottom". */
const BOTTOM_THRESHOLD = 8

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
  headerAction,
  className,
  dockInput = false,
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
  /** An optional control on the right of the title bar. */
  headerAction?: ReactNode
  className?: string
  /**
   * Pin the input row to the bottom of the panel, below a bottom-anchored
   * history that only follows new output while the reader is at its end.
   * Off by default: the prompt is then the last line of the scrollback stream.
   */
  dockInput?: boolean
}) {
  const panelRef = useRef<HTMLElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  const followOutput = useRef(true)
  const visibleLines = useMemo(() => linesAfterClear(lines), [lines])

  useEffect(() => {
    const container = outputRef.current
    if (!container) return
    // The docked history leaves the reader where they are while they read
    // earlier output; it resumes following once they scroll back down.
    if (dockInput && !followOutput.current) return
    container.scrollTop = container.scrollHeight
  }, [dockInput, visibleLines])

  function trackFollow() {
    const container = outputRef.current
    if (!container) return
    followOutput.current =
      container.scrollHeight - container.scrollTop - container.clientHeight <= BOTTOM_THRESHOLD
  }

  // Clicking anywhere in the scrollback focuses the prompt, like a real shell
  // (but never steal an in-progress text selection).
  function focusPrompt() {
    if (window.getSelection()?.toString()) return
    panelRef.current?.querySelector<HTMLInputElement>('[data-command-input]')?.focus()
  }

  const renderedLines = visibleLines.map((line) => (
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
  ))
  const input = (
    <CommandInput
      prompt={prompt}
      cwd={cwd}
      disabled={disabled}
      runDisabled={runDisabled}
      processing={processing}
      onSubmit={onCommand}
    />
  )

  return (
    <section
      ref={panelRef}
      aria-label={title}
      className={cn('terminal-panel', dockInput && 'terminal-panel--docked', className)}
    >
      <div className="terminal-titlebar workspace-panel-header">
        <span className="panel-eyebrow">{title}</span>
        {headerAction}
      </div>

      {dockInput ? (
        <>
          <div
            className="terminal-output terminal-output--docked app-scrollbar"
            ref={outputRef}
            role="log"
            aria-live="polite"
            aria-relevant="additions text"
            onClick={focusPrompt}
            onScroll={trackFollow}
          >
            <div className="terminal-history">{renderedLines}</div>
          </div>
          <div className="terminal-input-dock">{input}</div>
        </>
      ) : (
        /* The prompt is the last line of the stream, not a separate bar. */
        <div
          className="terminal-output app-scrollbar"
          ref={outputRef}
          role="log"
          aria-live="polite"
          aria-relevant="additions text"
          onClick={focusPrompt}
        >
          {renderedLines}
          {input}
        </div>
      )}
    </section>
  )
}
