import { AlertTriangle, Archive, Box, GitBranch, GitCommitHorizontal, ListTree, Target } from 'lucide-react'

import type { RepositoryValue } from '@/features/practice/types'
import { Card, CardContent, CardHeader } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

type LensEntry = {
  path?: string
  status?: string
  tokens?: string[]
  value?: RepositoryValue
}

type StateLens = Record<string, RepositoryValue>

type LensSection = {
  label: string
  items: string[]
  icon: typeof ListTree
}

export function StateLensPanel({
  title = 'Current State Lens',
  lens,
  delta,
  className,
  tone = 'current',
}: {
  title?: string
  lens?: StateLens | null
  delta?: StateLens | null
  className?: string
  tone?: 'current' | 'target'
}) {
  const sections = lensSections(lens ?? {})
  const changes = deltaSummary(delta ?? {})
  const colorClass = tone === 'target' ? 'text-amber-300' : 'text-primary'

  return (
    <Card className={cn('flex h-full min-h-0 flex-col overflow-hidden shadow-none', className)}>
      <CardHeader className="p-3">
        <div className="flex flex-wrap items-center gap-2">
          <Target className={cn('size-4', colorClass)} />
          <span className={cn('text-sm font-bold tracking-normal', colorClass)}>{title}</span>
        </div>
      </CardHeader>
      <CardContent className="min-h-0 flex-1 overflow-auto p-3 pt-0 app-scrollbar">
        <div className="grid gap-3 lg:grid-cols-2">
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <section className="rounded-md border border-border bg-background/35 p-3" key={section.label}>
                <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-normal text-muted-foreground">
                  <Icon className="size-3.5 text-primary" />
                  {section.label}
                </div>
                {section.items.length ? (
                  <ul className="grid gap-1.5 text-xs leading-5 text-muted-foreground">
                    {section.items.slice(0, 8).map((item) => (
                      <li className="truncate" title={item} key={item}>{item}</li>
                    ))}
                    {section.items.length > 8 ? <li>+{section.items.length - 8} more</li> : null}
                  </ul>
                ) : (
                  <p className="text-xs text-muted-foreground/70">None</p>
                )}
              </section>
            )
          })}
        </div>
        {changes.length ? (
          <section className="mt-3 rounded-md border border-primary/25 bg-primary/5 p-3">
            <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-normal text-primary">
              <AlertTriangle className="size-3.5" />
              Command Effect Delta
            </div>
            <ul className="grid gap-1.5 text-xs leading-5 text-muted-foreground sm:grid-cols-2">
              {changes.map((item) => (
                <li className="truncate" title={item} key={item}>{item}</li>
              ))}
            </ul>
          </section>
        ) : null}
      </CardContent>
    </Card>
  )
}

function lensSections(lens: StateLens): LensSection[] {
  return [
    {
      label: 'Working Directory',
      icon: ListTree,
      items: pathEntries(lens.working_directory),
    },
    {
      label: 'Staging Area',
      icon: Box,
      items: pathEntries(lens.staging_area),
    },
    {
      label: 'Local Repository',
      icon: GitCommitHorizontal,
      items: localRepositoryEntries(lens.local_repository),
    },
    {
      label: 'Branches',
      icon: GitBranch,
      items: recordEntries(lens.branch_pointers ?? lens.branches),
    },
    {
      label: 'Remotes',
      icon: Archive,
      items: [
        ...recordEntries(lens.remotes),
        ...recordEntries(lens.remote_tracking_branches, 'tracking'),
      ],
    },
    {
      label: 'Conflicts',
      icon: AlertTriangle,
      items: conflictEntries(lens.conflicts),
    },
  ]
}

function pathEntries(value: RepositoryValue | undefined): string[] {
  if (!Array.isArray(value)) return []
  return value
    .filter((entry): entry is LensEntry => Boolean(entry) && typeof entry === 'object' && !Array.isArray(entry))
    .map((entry) => {
      const tokens = Array.isArray(entry.tokens) && entry.tokens.length ? ` (${entry.tokens.join(', ')})` : ''
      return `${entry.path ?? 'unknown'} - ${entry.status ?? 'changed'}${tokens}`
    })
}

function localRepositoryEntries(value: RepositoryValue | undefined): string[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return []
  const record = value as Record<string, RepositoryValue>
  const items = []
  if (record.commit_count !== undefined) items.push(`${record.commit_count} commits`)
  if (record.head && typeof record.head === 'object' && !Array.isArray(record.head)) {
    const head = record.head as Record<string, RepositoryValue>
    items.push(`HEAD ${head.type}${head.name ? `:${head.name}` : ''}`)
  }
  return items
}

function recordEntries(value: RepositoryValue | undefined, prefix?: string): string[] {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return []
  return Object.entries(value).map(([key, item]) => `${prefix ? `${prefix} ` : ''}${key} -> ${formatValue(item)}`)
}

function conflictEntries(value: RepositoryValue | undefined): string[] {
  if (!Array.isArray(value)) return []
  return value.map((item) => {
    if (item && typeof item === 'object' && !Array.isArray(item)) {
      const record = item as Record<string, RepositoryValue>
      return String(record.path ?? 'conflict')
    }
    return String(item)
  })
}

function deltaSummary(delta: StateLens): string[] {
  return Object.entries(delta)
    .flatMap(([key, value]) => {
      if (Array.isArray(value)) {
        if (!value.length) return []
        return [`${humanize(key)}: ${value.map(formatValue).join(', ')}`]
      }
      if (typeof value === 'boolean') return value ? [humanize(key)] : []
      if (!value || value === '') return []
      return [`${humanize(key)}: ${formatValue(value)}`]
    })
}

function humanize(value: string) {
  return value.replaceAll('_', ' ')
}

function formatValue(value: RepositoryValue): string {
  if (value === null || value === undefined) return 'none'
  if (Array.isArray(value)) return value.map(formatValue).join(', ')
  if (typeof value === 'object') {
    const record = value as Record<string, RepositoryValue>
    if ('name' in record && 'before' in record && 'after' in record) {
      return `${record.name}: ${formatValue(record.before)} -> ${formatValue(record.after)}`
    }
    if ('id' in record) return String(record.id)
    return Object.entries(record).map(([key, item]) => `${key}: ${formatValue(item)}`).join(', ')
  }
  return String(value)
}
