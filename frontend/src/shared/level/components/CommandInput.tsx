import { Check, ClipboardPaste } from 'lucide-react'
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
  const [pasteStatus, setPasteStatus] = useState<'idle' | 'pasted' | 'empty' | 'unavailable'>('idle')
  const inputRef = useRef<HTMLInputElement>(null)
  const pasteResetTimerRef = useRef<number | null>(null)

  useEffect(() => {
    if (!disabled) inputRef.current?.focus()
  }, [disabled])

  useEffect(
    () => () => {
      if (pasteResetTimerRef.current !== null) {
        window.clearTimeout(pasteResetTimerRef.current)
      }
    },
    [],
  )

  function reportPaste(status: Exclude<typeof pasteStatus, 'idle'>) {
    setPasteStatus(status)
    if (pasteResetTimerRef.current !== null) {
      window.clearTimeout(pasteResetTimerRef.current)
    }
    pasteResetTimerRef.current = window.setTimeout(() => setPasteStatus('idle'), 1800)
  }

  async function pasteFromClipboard() {
    const input = inputRef.current
    if (!input || disabled) return

    try {
      const clipboardText = await navigator.clipboard?.readText()
      const text = (clipboardText ?? '').replace(/\r?\n+/g, ' ').trim()
      if (!text) {
        reportPaste(clipboardText === undefined ? 'unavailable' : 'empty')
        input.focus()
        return
      }

      const start = input.selectionStart ?? input.value.length
      const end = input.selectionEnd ?? start
      const nextValue = `${input.value.slice(0, start)}${text}${input.value.slice(end)}`
      const nextCaret = start + text.length
      setValue(nextValue)
      reportPaste('pasted')
      window.requestAnimationFrame(() => {
        input.focus()
        input.setSelectionRange(nextCaret, nextCaret)
      })
    } catch {
      reportPaste('unavailable')
      input.focus()
    }
  }

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
      <button
        type="button"
        className="command-input-paste"
        aria-label="Paste from clipboard"
        title="Paste from clipboard"
        disabled={disabled}
        onClick={pasteFromClipboard}
      >
        {pasteStatus === 'pasted' ? <Check aria-hidden="true" /> : <ClipboardPaste aria-hidden="true" />}
        <span>{pasteStatus === 'pasted' ? 'Pasted' : 'Paste'}</span>
      </button>
      <span className="sr-only" role="status" aria-live="polite">
        {pasteStatus === 'pasted' ? 'Pasted into command.' : null}
        {pasteStatus === 'empty' ? 'Clipboard is empty.' : null}
        {pasteStatus === 'unavailable'
          ? 'Clipboard access is unavailable. Use Control or Command plus V.'
          : null}
      </span>
    </form>
  )
}
