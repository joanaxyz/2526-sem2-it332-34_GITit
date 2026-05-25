import { AlertTriangle, BookOpenText, ClipboardList, Target } from 'lucide-react'
import type { ComponentType, ReactNode } from 'react'

import type { ScenarioSession, ScenarioStudentContext } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

export function ScenarioContextPanel({ session }: { session: ScenarioSession }) {
  const context = contextForSession(session)

  return (
    <Card className="shadow-none">
      <CardHeader className="p-3">
        <div className="flex flex-wrap gap-2">
          <Badge variant="blue">Module {session.module.number}</Badge>
          <Badge variant="default" className="capitalize">{session.difficulty}</Badge>
          {session.review_mode ? <Badge variant="warning">Review Mode</Badge> : null}
          {session.variant.changed_variant ? <Badge variant="warning">Changed variant</Badge> : null}
        </div>
        <CardTitle className="text-base leading-tight">{session.scenario.title}</CardTitle>
        <CardDescription>{session.scenario.focus}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3 p-3 pt-0">
        <Section icon={BookOpenText} title="Scenario Brief" hidden={!context.story}>
          <p className="text-sm leading-5 text-muted-foreground">{context.story}</p>
        </Section>

        <Section icon={ClipboardList} title="Repository Brief" hidden={session.difficulty !== 'easy' || !context.current_state.length}>
          <CompactList items={context.current_state} />
        </Section>

        <Section icon={Target} title="Required Details" hidden={!context.required_details.length}>
          <dl className="grid gap-2">
            {context.required_details.map((item) => (
              <div className="rounded-md border border-border bg-secondary/35 px-2.5 py-2" key={`${item.label}:${item.value}`}>
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
    <section className="rounded-md border border-border bg-background/40 p-2.5">
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
              tone === 'warning' && 'bg-destructive'
            )}
          />
          <span className={cn('min-w-0 text-muted-foreground', tone === 'warning' && 'text-foreground')}>{item}</span>
        </li>
      ))}
    </ul>
  )
}

function contextForSession(session: ScenarioSession) {
  const context = normalizeContext(session.student_context ?? session.scenario.student_context)
  const fallback = normalizeContext({
    story: session.scenario.narrative,
  })
  const hasStructuredContext =
    context.story ||
    context.current_state.length ||
    context.required_details.length ||
    context.constraints.length

  const active = hasStructuredContext ? context : fallback
  return {
    ...active,
    situation: active.situation,
  }
}

function normalizeContext(context?: ScenarioStudentContext | null) {
  return {
    story: cleanText(context?.story),
    situation: cleanText(context?.situation),
    current_state: cleanList(context?.current_state),
    required_details: (context?.required_details ?? [])
      .map((item) => ({ label: cleanText(item.label), value: cleanText(item.value) }))
      .filter((item) => item.label && item.value),
    constraints: cleanList(context?.constraints),
  }
}

function cleanList(values?: string[]) {
  return (values ?? []).map(cleanText).filter(Boolean)
}

function cleanText(value?: string) {
  return (value ?? '').trim()
}
