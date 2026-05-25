import { ChevronDown, ChevronRight, X } from 'lucide-react'

import type { PreviewCommand, PreviewNavGroup } from '@/features/scenarios/components/previewPayloadUtils'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

export function PreviewNavigator({
  groups,
  commands,
  activeCommandIndex,
  activePageIndex,
  collapsedGroups,
  onClose,
  onSelect,
  onToggleGroup,
}: {
  groups: PreviewNavGroup[]
  commands: PreviewCommand[]
  activeCommandIndex: number
  activePageIndex: number
  collapsedGroups: Record<string, boolean>
  onClose: () => void
  onSelect: (commandIndex: number, pageIndex: number) => void
  onToggleGroup: (groupId: string) => void
}) {
  return (
    <div className="absolute inset-0 z-20 bg-background/70 backdrop-blur-sm" role="dialog" aria-label="Command preview contents">
      <div className="flex h-full w-full max-w-md flex-col border-r border-border bg-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <div>
            <p className="text-xs font-semibold uppercase text-primary">Contents</p>
            <h4 className="text-base font-extrabold">Command guide</h4>
          </div>
          <Button type="button" size="icon" variant="ghost" onClick={onClose} aria-label="Close contents">
            <X className="size-4" />
          </Button>
        </div>
        <nav className="min-h-0 flex-1 overflow-y-auto p-3 app-scrollbar" aria-label="Command preview contents">
          {groups.map((group) => {
            const collapsed = Boolean(collapsedGroups[group.id])
            const active = group.commandIndexes.includes(activeCommandIndex)
            return (
              <section className="border-b border-border/70 py-2 last:border-b-0" key={group.id}>
                <button
                  aria-expanded={!collapsed}
                  className={cn(
                    'flex w-full min-w-0 items-center gap-2 rounded-md px-2 py-2 text-left transition hover:bg-secondary',
                    active && 'text-foreground',
                  )}
                  type="button"
                  onClick={() => onToggleGroup(group.id)}
                >
                  {collapsed ? <ChevronRight className="size-4 shrink-0" /> : <ChevronDown className="size-4 shrink-0" />}
                  <span className="min-w-0 flex-1 truncate font-mono text-sm font-bold">{group.title}</span>
                  <span className="rounded-sm border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground">
                    {group.commandIndexes.reduce((total, commandIndex) => total + commands[commandIndex].pages.length, 0)}
                  </span>
                </button>
                {!collapsed ? (
                  <div className="mt-1 grid gap-1 pl-6">
                    {group.commandIndexes.map((commandIndex) => {
                      const command = commands[commandIndex]
                      return command.pages.map((page, pageIndex) => {
                        const selected = commandIndex === activeCommandIndex && pageIndex === activePageIndex
                        const label = page.heading ?? page.title
                        return (
                          <button
                            aria-current={selected ? 'page' : undefined}
                            aria-label={`Open ${command.command || command.title}: ${label}`}
                            className={cn(
                              'grid min-h-12 min-w-0 rounded-md px-2 py-2 text-left transition hover:bg-secondary',
                              selected ? 'bg-primary/10 text-foreground' : 'text-muted-foreground',
                            )}
                            key={`${command.id}-${page.id ?? pageIndex}`}
                            type="button"
                            onClick={() => onSelect(commandIndex, pageIndex)}
                          >
                            <span className="truncate text-sm font-semibold">{label}</span>
                            <span className="truncate font-mono text-[11px]">{command.command || command.title}</span>
                          </button>
                        )
                      })
                    })}
                  </div>
                ) : null}
              </section>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
