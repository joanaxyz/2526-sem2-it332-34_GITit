import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

import type { TerminalPrompt } from '@/shared/level/terminalPrompt'

// A bare prompt line, like the reference mock: Enter submits, no button chrome.
export function CommandInput({
  prompt,
  disabled,
  runDisabled,
  processing,
  onSubmit,
}: {
  prompt: TerminalPrompt
  disabled?: boolean
  runDisabled?: boolean
  processing?: boolean
  onSubmit: (command: string) => void
}) {
  const [value, setValue] = useState('')
  const [history, setHistory] = useState<string[]>([])
  const [cursor, setCursor] = useState<number | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  function submit(event: FormEvent) {
    event.preventDefault()
    if (disabled || runDisabled) return
    const command = value.trim()
    if (!command) return
    setHistory((items) => [...items, command])
    setCursor(null)
    setValue('')
    onSubmit(command)
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      const next = cursor === null ? history.length - 1 : Math.max(0, cursor - 1)
      if (history[next]) {
        setCursor(next)
        setValue(history[next])
      }
    }
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      if (cursor === null) return
      const next = cursor + 1
      if (next >= history.length) {
        setCursor(null)
        setValue('')
      } else {
        setCursor(next)
        setValue(history[next])
      }
    }
  }

  return (
    <form
      className="command-input"
      onSubmit={submit}
    >
      <span className="command-input-prompt" aria-hidden="true">
        <span>{prompt.user}@{prompt.host}</span>
        <small>:</small>
        <b>{prompt.cwd}</b>
        <small>$ </small>
      </span>
      <input
        ref={inputRef}
        data-command-input
        aria-label="Git command"
        className="command-input-field"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        autoFocus
        placeholder={processing ? 'Processing command' : 'Type a git command'}
      />
    </form>
  )
}
