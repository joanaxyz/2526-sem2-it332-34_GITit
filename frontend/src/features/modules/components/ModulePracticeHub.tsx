import { useEffect, useRef } from 'react'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  BookOpenText,
  CheckCircle2,
  GitBranch,
  Lock,
  Milestone,
  Play,
  RefreshCcw,
  RotateCcw,
  Route,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { reviewApi } from '@/features/review/api/reviewApi'
import {
  scenariosApi,
  startPayloadForPractice,
  type PracticeStartPayload,
} from '@/features/scenarios/api/scenariosApi'
import type {
  CommandDrillAdventureSummary,
  CommandTopicSummary,
  ModuleContentPage,
  ModuleContentSection,
  PracticeAccess,
  PracticeActionIntent,
  WorkflowLevelAccess,
  WorkflowScenarioSummary,
} from '@/features/scenarios/types'
import type { LearningModule } from '@/features/modules/types'
import { syncPracticeSessionInCache } from '@/features/practice/utils/practiceCache'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/features/practice/utils/commandAccuracy'
import { Button } from '@/shared/components/Button'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

type ContentItem = CommandDrillAdventureSummary | CommandTopicSummary | WorkflowScenarioSummary

function useVisibleLoadMore(
  enabled: boolean,
  onVisible: () => void,
) {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!enabled || !ref.current) return
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) onVisible()
    }, { rootMargin: '260px' })
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
        limit: section === 'command_adventures' ? 1 : 4,
      }) as unknown as Promise<ModuleContentPage<T>>,
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
    <div className="flex min-w-[7.5rem] items-center gap-2">
      <span className="font-mono text-xs font-bold text-muted-foreground">
        {item.successful_attempts.count}/{item.successful_attempts.required}
      </span>
      <ProgressBar value={pct} className="h-1.5 flex-1" />
    </div>
  )
}

function statusClass(status: PracticeAccess['status']) {
  if (status === 'completed') return 'border-primary/35 bg-primary/10 text-primary'
  if (status === 'in_progress') return 'border-sky-400/35 bg-sky-400/10 text-sky-300'
  if (status === 'failed' || status === 'abandoned') return 'border-destructive/35 bg-destructive/10 text-destructive'
  if (status === 'locked') return 'border-border bg-muted/20 text-muted-foreground'
  return 'border-border bg-background/40 text-muted-foreground'
}

function StatusPill({ status }: { status: PracticeAccess['status'] }) {
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-bold capitalize leading-none', statusClass(status))}>
      {status.replace('_', ' ')}
    </span>
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
  enabled,
}: {
  module: LearningModule
  enabled: boolean
}) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const adventureQuery = useModuleContent<CommandDrillAdventureSummary>(module.id, 'command_adventures', enabled)
  const workflowQuery = useModuleContent<WorkflowScenarioSummary>(module.id, 'workflow_scenarios', enabled)

  const adventure = flattenPages(adventureQuery)[0] ?? null
  const workflowScenarios = flattenPages(workflowQuery)

  const workflowLoadRef = useVisibleLoadMore(
    Boolean(enabled && workflowQuery.hasNextPage && !workflowQuery.isFetchingNextPage),
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
    <section className="grid gap-4">
      <div className="grid gap-3 xl:grid-cols-[minmax(0,1.05fr)_minmax(24rem,0.95fr)]">
        <section className="rounded-md border border-primary/25 bg-background/45 p-4 shadow-none">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2 text-primary">
                <Route className="size-4" />
                <h3 className="text-sm font-extrabold uppercase tracking-normal">Command Drill Adventure</h3>
              </div>
              {adventure ? (
                <>
                  <h4 className="mt-2 text-xl font-extrabold leading-tight">{adventure.title}</h4>
                  <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">{adventure.description}</p>
                </>
              ) : null}
            </div>
            {adventure ? (
              <div className="min-w-[10rem]">
                <ProgressBar value={adventure.progress.value} className="h-1.5" glow />
                <p className="mt-1 font-mono text-xs text-muted-foreground">
                  {adventure.progress.levels_completed}/{adventure.progress.level_count} levels complete
                </p>
              </div>
            ) : null}
          </div>

          {adventureQuery.isLoading ? <div className="mt-4"><LoadingRows /></div> : null}
          {!adventureQuery.isLoading && !adventure ? <div className="mt-4"><EmptySection label="command adventures" /></div> : null}
          {adventure ? (
            <div className="mt-4 grid gap-2 sm:grid-cols-2 2xl:grid-cols-3">
              {adventure.levels.map((level) => (
                <CommandLevelButton
                  disabled={actionPending}
                  key={level.id}
                  level={level}
                  onAction={runPracticeAction}
                />
              ))}
            </div>
          ) : null}
        </section>

        <section className="rounded-md border border-border bg-background/35 p-4 shadow-none">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <GitBranch className="size-4 text-primary" />
              <h3 className="text-sm font-extrabold uppercase tracking-normal">Workflow Scenarios</h3>
            </div>
            <span className="font-mono text-xs text-muted-foreground">
              {module.workflow_scenario_count} scenarios
            </span>
          </div>
          {workflowQuery.isLoading ? <div className="mt-4"><LoadingRows /></div> : null}
          {!workflowQuery.isLoading && workflowScenarios.length === 0 ? <div className="mt-4"><EmptySection label="workflow scenarios" /></div> : null}
          <div className="mt-4 grid gap-3">
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
          {workflowQuery.isFetchingNextPage ? <div className="mt-3"><LoadingRows /></div> : null}
          {workflowQuery.hasNextPage ? (
            <Button className="mt-3" type="button" variant="ghost" size="sm" onClick={() => void workflowQuery.fetchNextPage()}>
              Load more workflow scenarios
            </Button>
          ) : null}
        </section>
      </div>
    </section>
  )
}

function CommandLevelButton({
  level,
  disabled,
  onAction,
}: {
  level: CommandDrillAdventureSummary['levels'][number]
  disabled: boolean
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const item = level.next_practice
  const action = item ? actionForPractice(item) : null
  const pct = level.progress.denominator
    ? Math.round((level.progress.numerator / level.progress.denominator) * 100)
    : 0

  return (
    <button
      type="button"
      className={cn(
        'group min-h-28 rounded-md border p-3 text-left transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
        level.status === 'completed'
          ? 'border-primary/45 bg-primary/10'
          : level.status === 'locked'
            ? 'border-border/60 bg-muted/20 opacity-70'
            : 'border-border bg-secondary/25 hover:border-primary/45 hover:bg-secondary/45',
      )}
      disabled={!item || !action || disabled}
      onClick={() => {
        if (item && action) onAction(item, action)
      }}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Milestone className={cn('size-4', level.status === 'locked' ? 'text-muted-foreground' : 'text-primary')} />
            <span className="text-base font-extrabold">{level.label}</span>
          </div>
          <p className="mt-1 text-xs leading-5 text-muted-foreground">
            {level.usage_count} usage{level.usage_count === 1 ? '' : 's'} / {level.variant_count} variant{level.variant_count === 1 ? '' : 's'}
          </p>
        </div>
        <StatusPill status={level.status} />
      </div>
      <div className="mt-3 flex items-center gap-2">
        <ProgressBar value={pct} className="h-1.5 flex-1" />
        <span className="font-mono text-xs text-muted-foreground">{level.progress.numerator}/{level.progress.denominator}</span>
      </div>
      <div className="mt-3 flex items-center justify-between gap-2 text-xs font-semibold text-muted-foreground">
        <span>{level.status === 'locked' ? 'Complete the previous level first' : actionLabel(action, item?.status ?? 'locked')}</span>
        {level.status === 'completed' ? <CheckCircle2 className="size-4 text-primary" /> : <ActionIcon action={action} status={item?.status ?? 'locked'} />}
      </div>
    </button>
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
    <article className="rounded-md border border-border bg-secondary/20 p-4">
      <div className="flex items-start gap-3">
        <BookOpenText className="mt-1 size-4 shrink-0 text-primary" />
        <div className="min-w-0 flex-1">
          <h4 className="text-base font-bold">{scenario.title}</h4>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">{scenario.summary}</p>
          {scenario.command_topics.length ? (
            <div className="mt-3 flex flex-wrap gap-2">
              {scenario.command_topics.map((topic) => (
                <span className="rounded-sm border border-border bg-background/45 px-2 py-1 font-mono text-[11px] text-muted-foreground" key={topic}>
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
    <div className={cn('rounded-md border bg-background/35 p-3', level.status === 'locked' ? 'border-border/50 opacity-65' : 'border-border')}>
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
