import { AlertTriangle, BookOpenText, CheckCircle2, ClipboardList, Info, Target } from 'lucide-react'
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
          <Badge variant="blue">Module {session.unit.number}</Badge>
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

        <Section icon={Info} title="Situation" hidden={session.difficulty === 'hard' || !context.situation}>
          <p className="text-sm leading-5 text-muted-foreground">{context.situation}</p>
        </Section>

        <Section icon={ClipboardList} title="Repository Brief" hidden={session.difficulty !== 'easy' || !context.current_state.length}>
          <CompactList items={context.current_state} />
        </Section>

        <Section icon={Target} title="Required Details" hidden={!context.provided_values.length}>
          <dl className="grid gap-2">
            {context.provided_values.map((item) => (
              <div className="rounded-md border border-border bg-secondary/35 px-2.5 py-2" key={`${item.label}:${item.value}`}>
                <dt className="text-[11px] font-bold uppercase text-muted-foreground">{item.label}</dt>
                <dd className="mt-0.5 break-words font-mono text-xs text-foreground">{item.value}</dd>
              </div>
            ))}
          </dl>
        </Section>

        {/* Success checklist removed as requested */}

        <Section icon={AlertTriangle} title="Constraints" hidden={!context.warnings.length}>
          <CompactList items={context.warnings} tone="warning" />
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
  marker = 'dot',
  tone = 'default',
}: {
  items: string[]
  marker?: 'dot' | 'check'
  tone?: 'default' | 'warning'
}) {
  return (
    <ul className="space-y-1.5 text-sm leading-5">
      {items.map((item) => (
        <li className="grid grid-cols-[auto_minmax(0,1fr)] gap-2" key={item}>
          <span
            className={cn(
              'mt-2 size-1.5 rounded-full bg-muted-foreground',
              marker === 'check' && 'mt-0.5 grid size-4 place-items-center rounded-full bg-primary/15 text-primary',
              tone === 'warning' && marker !== 'check' && 'bg-destructive'
            )}
          >
            {marker === 'check' ? <CheckCircle2 className="size-4" /> : null}
          </span>
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
    requirements: session.scenario.task_prompt ? [session.scenario.task_prompt] : [],
    inspection_suggestions: ['You may inspect the repository state before deciding what to do.'],
  })
  const hasStructuredContext =
    context.story ||
    context.current_state.length ||
    context.provided_values.length ||
    context.requirements.length ||
    context.warnings.length ||
    context.success_checklist.length ||
    context.inspection_suggestions.length

  const active = hasStructuredContext ? context : fallback
  return {
    ...active,
    situation: hasStructuredContext ? session.scenario.narrative : '',
  }
}

function normalizeContext(context?: ScenarioStudentContext | null) {
  return {
    story: cleanText(context?.story),
    current_state: cleanList(context?.current_state),
    provided_values: (context?.provided_values ?? [])
      .map((item) => ({ label: cleanText(item.label), value: cleanText(item.value) }))
      .filter((item) => item.label && item.value),
    requirements: cleanList(context?.requirements),
    warnings: cleanList(context?.warnings),
    success_checklist: cleanList(context?.success_checklist),
    inspection_suggestions: cleanList(context?.inspection_suggestions),
  }
}

function cleanList(values?: string[]) {
  return (values ?? []).map(cleanText).filter(Boolean)
}

function cleanText(value?: string) {
  return (value ?? '').trim()
}
