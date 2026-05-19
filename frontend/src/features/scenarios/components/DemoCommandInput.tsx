import { SendHorizontal } from 'lucide-react'
import { useState } from 'react'

import { Button } from '@/shared/components/Button'

export function DemoCommandInput({
  safeCommands,
  onCommand,
}: {
  safeCommands: string[]
  onCommand: (command: string) => void
}) {
  const [command, setCommand] = useState('')

  function submit(nextCommand = command) {
    const trimmed = nextCommand.trim()
    if (!trimmed) return
    onCommand(trimmed)
    setCommand('')
  }

  return (
    <div className="rounded-lg border border-border bg-background/40 p-3">
      <div className="mb-2 text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">Demo command input</div>
      <form
        className="flex items-center gap-2 rounded-md border border-border bg-secondary/40 px-3 py-2"
        onSubmit={(event) => {
          event.preventDefault()
          submit()
        }}
      >
        <span className="font-mono text-sm text-primary">$</span>
        <input
          aria-label="Demo command"
          className="min-w-0 flex-1 bg-transparent font-mono text-sm outline-none placeholder:text-muted-foreground"
          value={command}
          placeholder={safeCommands[0] ?? 'git status'}
          onChange={(event) => setCommand(event.target.value)}
        />
        <Button type="submit" size="sm" variant="outline">
          <SendHorizontal data-icon="inline-start" />
          Try
        </Button>
      </form>
      {safeCommands.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {safeCommands.map((safeCommand) => (
            <button
              className="rounded-full border border-border bg-secondary px-2.5 py-1 font-mono text-[11px] text-muted-foreground transition hover:border-primary/50 hover:text-foreground"
              key={safeCommand}
              type="button"
              onClick={() => submit(safeCommand)}
            >
              {safeCommand}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
