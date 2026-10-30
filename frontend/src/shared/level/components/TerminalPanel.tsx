import { ClipboardPaste } from 'lucide-react'
import { useEffect, useMemo, useRef } from 'react'
import type { ReactNode } from 'react'

import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'
import { CommandInput } from './CommandInput'
import type { CommandInputHandle } from './CommandInput'

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
}) {
  const panelRef = useRef<HTMLElement>(null)
  const outputRef = useRef<HTMLDivElement>(null)
  const commandInputRef = useRef<CommandInputHandle>(null)
  const followOutput = useRef(true)
  const visibleLines = useMemo(() => linesAfterClear(lines), [lines])

  useEffect(() => {
    const container = outputRef.current
    if (!container) return
    // Leave the reader in place while they read earlier output.
    if (!followOutput.current) return
    container.scrollTop = container.scrollHeight
  }, [visibleLines])

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
      ref={commandInputRef}
      prompt={prompt}
      cwd={cwd}
      disabled={disabled}
      runDisabled={runDisabled}
      processing={processing}
      onSubmit={(command) => {
        followOutput.current = true
        onCommand(command)
      }}
    />
  )

  return (
    <section
      ref={panelRef}
      aria-label={title}
      className={cn('terminal-panel', className)}
    >
      <div className="terminal-titlebar workspace-panel-header">
        <span className="panel-eyebrow">{title}</span>
        <div className="terminal-actions">
          {headerAction}
          <button
            type="button"
            className="terminal-paste"
            aria-label="Paste from clipboard"
            title="Paste from clipboard"
            disabled={disabled}
            onClick={() => void commandInputRef.current?.paste()}
          >
            <ClipboardPaste aria-hidden="true" />
            <span>Paste</span>
          </button>
        </div>
      </div>

      <div
        className="terminal-output app-scrollbar"
        ref={outputRef}
        role="log"
        aria-live="polite"
        aria-relevant="additions text"
        onClick={focusPrompt}
        onScroll={trackFollow}
      >
        {renderedLines}
        {input}
      </div>
    </section>
  )
}
