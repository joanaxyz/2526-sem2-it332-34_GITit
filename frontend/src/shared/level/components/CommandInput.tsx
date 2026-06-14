import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

import { Button } from '@/shared/components/Button'

export function CommandInput({
  disabled,
  runDisabled,
  processing,
  onSubmit,
}: {
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
      className="flex items-center gap-2 border-t border-white/[0.08] bg-[#131620] px-3 py-2"
      onSubmit={submit}
    >
      <span className="hidden shrink-0 font-mono text-[11px] md:inline-flex md:items-center" aria-hidden="true">
        <span className="text-emerald-400">student@git-it</span>
        <span className="text-muted-foreground/55">:</span>
        <span className="text-primary">~</span>
        <span className="text-muted-foreground/55"> $ </span>
      </span>
      <input
        ref={inputRef}
        data-command-input
        className="h-7 min-w-0 flex-1 bg-transparent font-mono text-xs text-foreground caret-primary outline-none placeholder:text-muted-foreground/35"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        autoFocus
        placeholder={processing ? 'Processing command' : 'Type a git command'}
      />
      <Button type="submit" size="sm" disabled={disabled || runDisabled}>
        {processing ? 'Running' : 'Run'}
      </Button>
    </form>
  )
}
