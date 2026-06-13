import { AlertTriangle, BookOpenText, Check, ClipboardList, Target } from 'lucide-react'
import type { ComponentType, ReactNode } from 'react'

import type { ChallengeRun } from '@/shared/level/types'
import {
  hasLevelContext,
  normalizeLevelContext,
  type NormalizedLevelContext,
  type ObjectiveCheck,
} from '@/shared/level/utils/levelContext'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

export function LevelContextPanel({ run }: { run: ChallengeRun }) {
  const context = contextForRun(run)
  const difficultyLabel = run.difficulty ? run.difficulty : 'challenge'

  return (
    <LevelBriefCard
      title={run.challenge.title}
      context={context}
      badges={
        <>
          <Badge variant="blue">Storey {run.storey.number}</Badge>
          <Badge variant="default" className="capitalize">{difficultyLabel}</Badge>
          {run.review_mode ? <Badge variant="warning">Review Mode</Badge> : null}
          {run.variant.changed_variant ? <Badge variant="warning">Changed variant</Badge> : null}
        </>
      }
    />
  )
}

/**
 * Presentational scenario brief shared by the challenge and adventure workspaces.
 * Renders a normalized context; callers supply the heading and any badges.
 *
 * The live objective checklist is an adventure-only scaffold and is not part of
 * the scenario context: the adventure caller passes the evaluated rows via
 * `checks`. Challenges pass none and rely on the expected-state reveal instead.
 */
export function LevelBriefCard({
  title,
  context,
  badges,
  className,
  checks,
}: {
  title: string
  context: NormalizedLevelContext
  badges?: ReactNode
  className?: string
  checks?: ObjectiveCheck[]
}) {
  return (
    <Card className={cn('shadow-none', className)}>
      <CardHeader className="p-3">
        {badges ? <div className="flex flex-wrap gap-2">{badges}</div> : null}
        <CardTitle className="text-base leading-tight">{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 p-3 pt-0">
        <Section icon={BookOpenText} title="Level brief" hidden={!context.story && !context.task}>
          {context.story ? <p className="text-sm leading-5 text-muted-foreground">{context.story}</p> : null}
          {context.task ? <p className="mt-2 text-sm leading-5 text-foreground">{context.task}</p> : null}
        </Section>

        <Section icon={Target} title="Objective" hidden={!checks?.length}>
          <ul className="space-y-1.5 text-sm leading-5">
            {(checks ?? []).map((check) => (
              <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-2" key={check.label}>
                {check.satisfied ? (
                  <span className="mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Check className="size-3" />
                  </span>
                ) : (
                  <span className="mt-0.5 size-4 shrink-0 rounded-full border border-muted-foreground/40" />
                )}
                <span
                  className={cn(
                    'min-w-0',
                    check.satisfied
                      ? 'text-foreground line-through decoration-muted-foreground/40'
                      : 'text-muted-foreground',
                  )}
                >
                  {check.label}
                </span>
              </li>
            ))}
          </ul>
        </Section>

        <Section icon={ClipboardList} title="Key details" hidden={!context.details.length}>
          <dl className="grid gap-2">
            {context.details.map((item) => (
              <div className="rounded-md border border-border bg-secondary/35 px-3 py-2.5" key={`${item.label}:${item.value}`}>
                <dt className="text-[11px] font-bold uppercase text-muted-foreground">{item.label}</dt>
                <dd className="mt-0.5 break-words font-mono text-xs text-foreground">{item.value}</dd>
              </div>
            ))}
          </dl>
        </Section>

        <Section icon={AlertTriangle} title="Constraints" hidden={!context.constraints.length}>
          <CompactList items={context.constraints} tone="warning" />
        </Section>
      </CardContent>
    </Card>
  )
}

function Section({
  children,
  hidden,
  icon: Icon,
  title,
}: {
  children: ReactNode
  hidden?: boolean
  icon: ComponentType<{ className?: string }>
  title: string
}) {
  if (hidden) return null
  return (
    <section className="rounded-md border border-border bg-background/40 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-normal text-muted-foreground">
        <Icon className="size-3.5 text-primary" />
        {title}
      </div>
      {children}
    </section>
  )
}

function CompactList({
  items,
  tone = 'default',
}: {
  items: string[]
  tone?: 'default' | 'warning'
}) {
  return (
    <ul className="space-y-1.5 text-sm leading-5">
      {items.map((item) => (
        <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-2" key={item}>
          <span
            className={cn(
              'mt-2 size-1.5 rounded-full bg-muted-foreground',
              tone === 'warning' && 'bg-destructive',
            )}
          />
          <span className={cn('min-w-0 text-muted-foreground', tone === 'warning' && 'text-foreground')}>{item}</span>
        </li>
      ))}
    </ul>
  )
}

function contextForRun(run: ChallengeRun) {
  const context = normalizeLevelContext(run.scenario_context)
  const fallback = normalizeLevelContext({
    story: run.challenge.narrative,
    task: run.challenge.summary,
  })

  return hasLevelContext(context) ? context : fallback
}
