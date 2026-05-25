import { X } from 'lucide-react'

import {
  navigationAnchorsForCommand,
  type PreviewCommand,
  type PreviewNavGroup,
} from '@/features/scenarios/components/previewPayloadUtils'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

export function PreviewNavigator({
  groups,
  commands,
  activeCommandIndex,
  onClose,
  onSelect,
}: {
  groups: PreviewNavGroup[]
  commands: PreviewCommand[]
  activeCommandIndex: number
  onClose: () => void
  onSelect: (commandIndex: number, anchorId?: string) => void
}) {
  return (
    <div className="absolute inset-0 z-20 bg-background/70 backdrop-blur-sm" role="dialog" aria-label="Command contents">
      <div className="flex h-full w-full max-w-sm flex-col border-r border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h4 className="text-base font-extrabold">Commands</h4>
          <Button type="button" size="icon" variant="ghost" onClick={onClose} aria-label="Close contents">
            <X className="size-4" />
          </Button>
        </div>
        <nav className="min-h-0 flex-1 overflow-y-auto p-3 app-scrollbar" aria-label="Command contents">
          <div className="grid gap-2">
            {groups.map((group) => (
              <section className="grid gap-1 border-b border-border/70 pb-2 last:border-b-0 last:pb-0" key={group.id}>
                {group.commandIndexes.map((commandIndex) => {
                  const command = commands[commandIndex]
                  const selected = commandIndex === activeCommandIndex
                  const label = command.command || command.title || group.title
                  const displayLabel = commandDisplayLabel(label, group.title, group.commandIndexes.length > 1)
                  const anchors = navigationAnchorsForCommand(command)
                  return (
                    <div className="grid gap-1" key={command.id}>
                      <button
                        aria-current={selected ? 'page' : undefined}
                        aria-label={`Open ${label}`}
                        className={cn(
                          'min-h-10 min-w-0 rounded-md px-2 py-2 text-left font-mono text-sm font-bold transition hover:bg-secondary',
                          selected ? 'bg-primary/10 text-foreground' : 'text-muted-foreground',
                        )}
                        type="button"
                        onClick={() => onSelect(commandIndex)}
                      >
                        <span className="block truncate">{displayLabel}</span>
                      </button>
                      {anchors.length ? (
                        <div className="grid gap-0.5 pl-4">
                          {anchors.map((anchor) => (
                            <button
                              aria-label={`Jump to ${label} ${anchor.label}`}
                              className="min-h-8 min-w-0 rounded-sm px-2 py-1.5 text-left font-mono text-xs text-muted-foreground transition hover:bg-secondary hover:text-foreground"
                              key={`${command.id}-${anchor.id}`}
                              type="button"
                              onClick={() => onSelect(commandIndex, anchor.id)}
                            >
                              <span className="block truncate">{anchor.label}</span>
                            </button>
                          ))}
                        </div>
                      ) : null}
                    </div>
                  )
                })}
              </section>
            ))}
          </div>
        </nav>
      </div>
    </div>
  )
}

function commandDisplayLabel(label: string, groupTitle: string, grouped: boolean) {
  if (!grouped) return label
  const normalizedLabel = label.toLowerCase()
  const normalizedGroup = groupTitle.toLowerCase()
  if (normalizedLabel.startsWith(normalizedGroup) && normalizedLabel !== normalizedGroup) {
    return label.slice(groupTitle.length).trim()
  }
  return label
}
