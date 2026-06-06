import { useEffect, useRef, useState } from 'react'
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpenText, CheckCircle2, Command, Eye, GitBranch, Loader2, Lock, Play, RefreshCcw, RotateCcw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import {
  scenariosApi,
  startPayloadForPractice,
  type PracticeStartPayload,
} from '@/features/scenarios/api/scenariosApi'
import type {
  CommandDrillAccess,
  CommandTopicSummary,
  CommandUsageSummary,
  ModuleContentSection,
  PracticeAccess,
  PracticeActionIntent,
  WorkflowLevelAccess,
  WorkflowScenarioSummary,
} from '@/features/scenarios/types'
import type { LearningModule } from '@/features/modules/types'
import { syncPracticeSessionInCache } from '@/features/scenarios/utils/scenarioCache'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/features/scenarios/utils/commandAccuracy'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

type ContentItem = CommandTopicSummary | WorkflowScenarioSummary

function useVisibleLoadMore(
  enabled: boolean,
  onVisible: () => void,
) {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!enabled || !ref.current) return
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) onVisible()
    }, { rootMargin: '240px' })
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [enabled, onVisible])

  return ref
}

function useModuleContent<T extends ContentItem>(
  moduleId: number,
  section: ModuleContentSection,
  enabled: boolean,
) {
  return useInfiniteQuery({
    queryKey: queryKeys.moduleContent(moduleId, section),
    queryFn: ({ pageParam }) =>
      scenariosApi.moduleContent(moduleId, section, {
        cursor: typeof pageParam === 'number' ? pageParam : null,
        limit: 4,
      }) as unknown as Promise<{ results: T[]; next_cursor: number | null }>,
    initialPageParam: null as number | null,
    getNextPageParam: (lastPage) => lastPage.next_cursor,
    enabled,
    staleTime: 2 * 60 * 1000,
  })
}

function actionForPractice(item: PracticeAccess): PracticeActionIntent | null {
  if (item.status === 'locked') return null
  if (item.status === 'in_progress') return item.active_session_id ? 'resume' : null
  if (item.status === 'completed') {
    const progressComplete = item.successful_attempts.count >= item.successful_attempts.required
    const latestAccuracy = item.latest_attempt?.accuracy_rate ?? null
    if (item.review_available && progressComplete && meetsMasteryAccuracy(latestAccuracy)) return 'review'
    if (meetsProgressAccuracy(latestAccuracy)) return 'continue'
    return 'retry'
  }
  if (item.status === 'failed' || item.status === 'abandoned') return 'retry'
  return 'start'
}

function actionLabel(action: PracticeActionIntent | null, status: PracticeAccess['status']) {
  if (status === 'locked') return 'Locked'
  if (action === 'review') return 'Review'
  if (action === 'continue' || action === 'resume') return 'Continue'
  if (action === 'retry') return 'Retry'
  return 'Start'
}

function ActionIcon({ action, status }: { action: PracticeActionIntent | null; status: PracticeAccess['status'] }) {
  const Icon =
    status === 'locked'
      ? Lock
      : action === 'review'
        ? RotateCcw
        : action === 'retry'
          ? RefreshCcw
          : Play
  return <Icon data-icon="inline-start" />
}

function progressText(item: PracticeAccess) {
  return `${item.successful_attempts.count}/${item.successful_attempts.required}`
}

function statusClass(status: PracticeAccess['status']) {
  if (status === 'completed') return 'border-primary/35 bg-primary/10 text-primary'
  if (status === 'in_progress') return 'border-sky-400/35 bg-sky-400/10 text-sky-300'
  if (status === 'failed' || status === 'abandoned') return 'border-destructive/35 bg-destructive/10 text-destructive'
  if (status === 'locked') return 'border-border bg-muted/20 text-muted-foreground'
  return 'border-border bg-background/40 text-muted-foreground'
}

function PracticeActionButton({
  item,
  disabled,
  onAction,
}: {
  item: PracticeAccess
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const action = actionForPractice(item)
  return (
    <Button
      type="button"
      size="sm"
      variant={action === 'start' || action === 'continue' || action === 'resume' ? 'default' : 'outline'}
      disabled={!action || disabled}
      onClick={() => {
        if (action) onAction(item, action)
      }}
    >
      <ActionIcon action={action} status={item.status} />
      {actionLabel(action, item.status)}
    </Button>
  )
}

function PracticeProgress({ item }: { item: PracticeAccess }) {
  const pct = item.successful_attempts.required
    ? Math.round((item.successful_attempts.count / item.successful_attempts.required) * 100)
    : 0
  return (
    <div className="flex min-w-[8.5rem] items-center gap-2">
      <span className="font-mono text-xs font-bold text-muted-foreground">{progressText(item)}</span>
      <ProgressBar value={pct} className="h-1.5 flex-1" />
    </div>
  )
}

function StatusPill({ status }: { status: PracticeAccess['status'] }) {
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold capitalize leading-none', statusClass(status))}>
      {status.replace('_', ' ')}
    </span>
  )
}

function CommandPreviewModal({
  usageId,
  onClose,
}: {
  usageId: number | null
  onClose: () => void
}) {
  const open = usageId !== null
  const query = useQuery({
    queryKey: usageId ? queryKeys.commandUsagePreview(usageId) : ['command-usage-preview', null],
    queryFn: () => scenariosApi.commandUsagePreview(usageId ?? 0),
    enabled: open,
    staleTime: 5 * 60 * 1000,
  })
  const preview = query.data?.command_preview
  const pages = preview?.pages ?? []

  return (
    <Modal open={open} title={query.data?.label ?? 'Command preview'} className="w-full max-w-3xl" onClose={onClose}>
      {query.isLoading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          Loading command preview
        </div>
      ) : query.isError ? (
        <p className="text-sm text-destructive">{query.error.message}</p>
      ) : (
        <div className="space-y-5">
          <div>
            <p className="font-mono text-xs text-primary">{query.data?.topic.base_command}</p>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              {preview?.intro ?? preview?.purpose ?? query.data?.summary}
            </p>
          </div>
          {preview?.syntax_examples?.length ? (
            <section>
              <h3 className="text-sm font-bold">Syntax</h3>
              <div className="mt-2 grid gap-2">
                {preview.syntax_examples.map((example) => (
                  <code className="rounded-md border border-border bg-secondary/45 px-3 py-2 font-mono text-xs" key={example}>
                    {example}
                  </code>
                ))}
              </div>
            </section>
          ) : null}
          {pages.map((page) => (
            <section className="rounded-md border border-border bg-background/35 p-3" key={page.id ?? page.title}>
              <h3 className="text-sm font-bold">{page.title}</h3>
              {page.body ? <p className="mt-2 text-sm leading-6 text-muted-foreground">{page.body}</p> : null}
              {page.blocks?.map((block, index) => (
                <div className="mt-3 text-sm leading-6 text-muted-foreground" key={`${page.title}-${index}`}>
                  {block.title ? <p className="font-semibold text-foreground">{block.title}</p> : null}
                  {block.command ? <code className="font-mono text-primary">{block.command}</code> : null}
                  {block.body ?? block.text ? <p>{block.body ?? block.text}</p> : null}
                  {block.items?.length ? (
                    <ul className="mt-1 grid gap-1">
                      {block.items.map((item) => <li key={item}>{item}</li>)}
                    </ul>
                  ) : null}
                </div>
              ))}
            </section>
          ))}
          {preview?.common_mistakes?.length ? (
            <section>
              <h3 className="text-sm font-bold">Common mistakes</h3>
              <ul className="mt-2 grid gap-1 text-sm leading-6 text-muted-foreground">
                {preview.common_mistakes.map((item) => <li key={item}>{item}</li>)}
              </ul>
            </section>
          ) : null}
        </div>
      )}
    </Modal>
  )
}

function EmptySection({ label }: { label: string }) {
  return (
    <div className="rounded-md border border-dashed border-border bg-background/30 px-4 py-5 text-sm text-muted-foreground">
      No {label} published yet.
    </div>
  )
}

function LoadingRows() {
  return (
    <div className="grid gap-2">
      {Array.from({ length: 3 }, (_, index) => (
        <div className="h-16 animate-pulse rounded-md border border-border bg-secondary/30" key={index} />
      ))}
    </div>
  )
}

function flattenPages<T extends ContentItem>(query: ReturnType<typeof useModuleContent<T>>) {
  return query.data?.pages.flatMap((page) => page.results) ?? []
}

export function ModulePracticeHub({
  module,
  expanded,
}: {
  module: LearningModule
  expanded: boolean
}) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [previewUsageId, setPreviewUsageId] = useState<number | null>(null)
  const commandQuery = useModuleContent<CommandTopicSummary>(module.id, 'command_topics', expanded)
  const workflowQuery = useModuleContent<WorkflowScenarioSummary>(module.id, 'workflow_scenarios', expanded)

  const commandTopics = flattenPages(commandQuery)
  const workflowScenarios = flattenPages(workflowQuery)

  const commandLoadRef = useVisibleLoadMore(
    Boolean(commandQuery.hasNextPage && !commandQuery.isFetchingNextPage),
    () => void commandQuery.fetchNextPage(),
  )
  const workflowLoadRef = useVisibleLoadMore(
    Boolean(workflowQuery.hasNextPage && !workflowQuery.isFetchingNextPage),
    () => void workflowQuery.fetchNextPage(),
  )

  const startMutation = useMutation({
    mutationFn: (payload: PracticeStartPayload) => scenariosApi.startSession(payload),
    onSuccess: (session) => {
      syncPracticeSessionInCache(queryClient, session)
      navigate(`/practice/${session.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (payload: PracticeStartPayload) => reviewApi.startReviewSession(payload),
    onSuccess: (session) => {
      syncPracticeSessionInCache(queryClient, session)
      navigate(`/review/${session.id}`)
    },
  })

  function runPracticeAction(item: PracticeAccess, action: PracticeActionIntent) {
    if (action === 'resume' && item.active_session_id) {
      navigate(`/practice/${item.active_session_id}`)
      return
    }
    const payload = startPayloadForPractice(item.practice_kind, item.id, action === 'review' ? 'review' : 'module_page')
    if (action === 'review') {
      reviewMutation.mutate(payload)
      return
    }
    startMutation.mutate(payload)
  }

  const actionPending = startMutation.isPending || reviewMutation.isPending

  return (
    <section className="grid gap-6">
      <div className="grid gap-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Command className="size-4 text-primary" />
            <h3 className="text-sm font-extrabold uppercase tracking-normal">Command drills</h3>
          </div>
          <span className="font-mono text-xs text-muted-foreground">
            {module.command_topic_count} topics
          </span>
        </div>
        {commandQuery.isLoading ? <LoadingRows /> : null}
        {!commandQuery.isLoading && commandTopics.length === 0 ? <EmptySection label="command drills" /> : null}
        <div className="grid gap-4">
          {commandTopics.map((topic) => (
            <CommandTopicCard
              disabled={actionPending}
              key={topic.id}
              topic={topic}
              onAction={runPracticeAction}
              onPreview={setPreviewUsageId}
            />
          ))}
        </div>
        <div ref={commandLoadRef} />
        {commandQuery.isFetchingNextPage ? <LoadingRows /> : null}
        {commandQuery.hasNextPage ? (
          <Button type="button" variant="ghost" size="sm" onClick={() => void commandQuery.fetchNextPage()}>
            Load more command topics
          </Button>
        ) : null}
      </div>

      <div className="grid gap-3 border-t border-border/60 pt-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <GitBranch className="size-4 text-primary" />
            <h3 className="text-sm font-extrabold uppercase tracking-normal">Workflow scenarios</h3>
          </div>
          <span className="font-mono text-xs text-muted-foreground">
            {module.workflow_scenario_count} scenarios
          </span>
        </div>
        {workflowQuery.isLoading ? <LoadingRows /> : null}
        {!workflowQuery.isLoading && workflowScenarios.length === 0 ? <EmptySection label="workflow scenarios" /> : null}
        <div className="grid gap-3">
          {workflowScenarios.map((scenario) => (
            <WorkflowScenarioCard
              disabled={actionPending}
              key={scenario.id}
              scenario={scenario}
              onAction={runPracticeAction}
            />
          ))}
        </div>
        <div ref={workflowLoadRef} />
        {workflowQuery.isFetchingNextPage ? <LoadingRows /> : null}
        {workflowQuery.hasNextPage ? (
          <Button type="button" variant="ghost" size="sm" onClick={() => void workflowQuery.fetchNextPage()}>
            Load more workflow scenarios
          </Button>
        ) : null}
      </div>

      <CommandPreviewModal usageId={previewUsageId} onClose={() => setPreviewUsageId(null)} />
    </section>
  )
}

function CommandTopicCard({
  topic,
  disabled,
  onAction,
  onPreview,
}: {
  topic: CommandTopicSummary
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
  onPreview: (usageId: number) => void
}) {
  return (
    <article className="rounded-md border border-border bg-background/35 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-primary">{topic.base_command}</p>
          <h4 className="mt-1 text-base font-bold">{topic.title}</h4>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-muted-foreground">{topic.summary}</p>
        </div>
        <div className="min-w-[9rem]">
          <ProgressBar value={topic.progress.value} className="h-1.5" />
          <p className="mt-1 font-mono text-xs text-muted-foreground">
            {topic.progress.numerator}/{topic.progress.denominator}
          </p>
        </div>
      </div>
      <div className="mt-4 grid gap-3">
        {topic.usages.map((usage) => (
          <CommandUsageCard
            disabled={disabled}
            key={usage.id}
            usage={usage}
            onAction={onAction}
            onPreview={onPreview}
          />
        ))}
      </div>
    </article>
  )
}

function CommandUsageCard({
  usage,
  disabled,
  onAction,
  onPreview,
}: {
  usage: CommandUsageSummary
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
  onPreview: (usageId: number) => void
}) {
  return (
    <div className="rounded-md border border-border/70 bg-secondary/25 p-3">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-mono text-xs text-primary">{usage.usage_form}</p>
          <h5 className="mt-1 text-sm font-bold">{usage.label}</h5>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{usage.summary}</p>
        </div>
        <Button type="button" variant="ghost" size="sm" onClick={() => onPreview(usage.id)}>
          <Eye data-icon="inline-start" />
          Preview
        </Button>
      </div>
      <div className="mt-3 grid gap-2">
        {usage.drills.map((drill) => (
          <CommandDrillRow
            disabled={disabled}
            drill={drill}
            key={drill.id}
            onAction={onAction}
          />
        ))}
      </div>
    </div>
  )
}

function CommandDrillRow({
  drill,
  disabled,
  onAction,
}: {
  drill: CommandDrillAccess
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-background/45 px-3 py-2">
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2">
          <h6 className="text-sm font-semibold">{drill.title}</h6>
          <StatusPill status={drill.status} />
          {drill.completion?.first_attempt_star ? <CheckCircle2 className="size-4 text-primary" /> : null}
        </div>
        <p className="mt-1 max-w-3xl text-xs leading-5 text-muted-foreground">{drill.summary}</p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <PracticeProgress item={drill} />
        <PracticeActionButton disabled={disabled} item={drill} onAction={onAction} />
      </div>
    </div>
  )
}

function WorkflowScenarioCard({
  scenario,
  disabled,
  onAction,
}: {
  scenario: WorkflowScenarioSummary
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  return (
    <article className="rounded-md border border-border bg-background/35 p-4">
      <div className="flex items-start gap-3">
        <BookOpenText className="mt-1 size-4 shrink-0 text-primary" />
        <div className="min-w-0 flex-1">
          <h4 className="text-base font-bold">{scenario.title}</h4>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{scenario.summary}</p>
          {scenario.command_topics.length ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {scenario.command_topics.map((topic) => (
                <span className="rounded-sm border border-border bg-secondary/35 px-2 py-1 font-mono text-[11px] text-muted-foreground" key={topic}>
                  {topic}
                </span>
              ))}
            </div>
          ) : null}
        </div>
      </div>
      <div className="mt-4 grid gap-2 md:grid-cols-3">
        {scenario.levels.map((level) => (
          <WorkflowLevelCard
            disabled={disabled}
            key={level.id}
            level={level}
            onAction={onAction}
          />
        ))}
      </div>
    </article>
  )
}

function WorkflowLevelCard({
  level,
  disabled,
  onAction,
}: {
  level: WorkflowLevelAccess
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const latestAccuracy = level.latest_attempt?.accuracy_rate
  return (
    <div className={cn('rounded-md border bg-secondary/20 p-3', level.status === 'locked' ? 'border-border/50 opacity-65' : 'border-border')}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <p className="text-sm font-bold capitalize">{level.difficulty}</p>
          <StatusPill status={level.status} />
        </div>
        {latestAccuracy !== null && latestAccuracy !== undefined ? (
          <span className="font-mono text-sm font-bold text-muted-foreground">{latestAccuracy}%</span>
        ) : null}
      </div>
      <div className="mt-3">
        <PracticeProgress item={level} />
      </div>
      <div className="mt-3">
        <PracticeActionButton disabled={disabled} item={level} onAction={onAction} />
      </div>
    </div>
  )
}
