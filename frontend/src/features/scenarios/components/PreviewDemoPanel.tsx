import { SquareTerminal } from 'lucide-react'

import type { RepositorySnapshot, TerminalLine } from '@/features/practice/types'
import { TerminalPanel } from '@/features/practice/components/TerminalPanel'
import { DemoLiveDagPanel } from '@/features/scenarios/components/DemoLiveDagPanel'

export function PreviewDemoPanel({
  commands,
  disabled,
  lines,
  snapshot,
  onCommand,
}: {
  commands: string[]
  disabled: boolean
  lines: TerminalLine[]
  snapshot: RepositorySnapshot
  onCommand: (command: string) => void
}) {
  return (
    <div className="mx-auto grid max-w-4xl gap-4">
      <DemoLiveDagPanel snapshot={snapshot} />
      <section className="grid gap-3">
        <div className="rounded-md border border-border bg-card p-4">
          <h5 className="flex items-center gap-2 text-sm font-bold">
            <SquareTerminal className="size-4 text-primary" />
            Try it
          </h5>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Run any preview command here. This is a shared demo, separate from scenario attempts.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {commands.map((command) => (
              <button
                className="rounded-sm border border-border bg-secondary/30 px-2 py-1 font-mono text-[11px] text-muted-foreground hover:text-foreground"
                key={command}
                type="button"
                onClick={() => onCommand(command)}
              >
                {command}
              </button>
            ))}
          </div>
        </div>
        <TerminalPanel
          title="Inline command demo"
          className="h-72 rounded-md"
          disabled={disabled}
          lines={lines}
          onCommand={onCommand}
        />
      </section>
    </div>
  )
}
