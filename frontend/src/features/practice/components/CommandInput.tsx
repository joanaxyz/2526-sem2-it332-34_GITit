import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

import { Button } from '@/shared/components/Button'

export function CommandInput({
  disabled,
  onSubmit,
}: {
  disabled?: boolean
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
    if (disabled) return
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
    <form className="flex gap-2 border-t border-border p-2" onSubmit={submit}>
      <span className="hidden pt-2 font-mono text-[11px] text-primary md:block">student@git-it $</span>
      <input
        ref={inputRef}
        className="h-9 min-w-0 flex-1 rounded-md border border-input bg-background px-3 font-mono text-xs outline-none focus:ring-2 focus:ring-ring"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        autoFocus
        placeholder="Type a git command"
      />
      <Button type="submit" size="sm" disabled={disabled}>Run</Button>
    </form>
  )
}
