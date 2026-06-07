import { useEffect, useMemo, useRef } from 'react'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  CheckCircle2,
  ChevronsUp,
  CircleDotDashed,
  Flag,
  GitBranch,
  GitCommitHorizontal,
  Lock,
  MapPinned,
  Play,
  RefreshCcw,
  RotateCcw,
  Swords,
  TerminalSquare,
  Trophy,
  type LucideIcon,
} from 'lucide-react'
import { motion, useInView } from 'motion/react'
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

const CHALLENGE_ICONS: LucideIcon[] = [Flag, Swords, Trophy, GitBranch, MapPinned]
const DIFFICULTY_COPY: Record<string, { label: string; hint: string }> = {
  easy: { label: 'Easy', hint: 'Guided' },
  medium: { label: 'Medium', hint: 'Less help' },
  hard: { label: 'Hard', hint: 'DAG only' },
}

function useVisibleLoadMore(enabled: boolean, onVisible: () => void) {
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!enabled || !ref.current) return
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) onVisible()
    }, { rootMargin: '320px' })
    observer.observe(ref.current)
    return () => observer.disconnect()
  }, [enabled, onVisible])

  return ref
}

function useModuleContent<T extends ContentItem>(moduleId: number, section: ModuleContentSection, enabled: boolean) {
  return useInfiniteQuery({
    queryKey: queryKeys.moduleContent(moduleId, section),
    queryFn: ({ pageParam }) =>
      scenariosApi.moduleContent(moduleId, section, {
        cursor: typeof pageParam === 'number' ? pageParam : null,
        limit: section === 'command_adventures' ? 1 : 6,
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
  className,
  onAction,
}: {
  item: PracticeAccess
  disabled: boolean
  className?: string
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const action = actionForPractice(item)
  return (
    <Button
      type="button"
      size="sm"
      className={className}
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

function PracticeProgress({ item, compact = false }: { item: PracticeAccess; compact?: boolean }) {
  const pct = item.successful_attempts.required
    ? Math.round((item.successful_attempts.count / item.successful_attempts.required) * 100)
    : 0
  return (
    <div className={cn('flex items-center gap-2', compact ? 'min-w-[5.5rem]' : 'min-w-[7.5rem]')}>
      <ProgressBar value={pct} className="h-1.5 flex-1" glow={item.status !== 'locked'} />
      <span className="font-mono text-[11px] text-muted-foreground">
        {item.successful_attempts.count}/{item.successful_attempts.required}
      </span>
    </div>
  )
}

function statusClass(status: PracticeAccess['status']) {
  if (status === 'completed') return 'border-primary/35 bg-primary/10 text-primary'
  if (status === 'in_progress') return 'border-accent/35 bg-accent/10 text-accent'
  if (status === 'failed' || status === 'abandoned') return 'border-accent/25 bg-accent/5 text-accent'
  if (status === 'locked') return 'border-border bg-muted/20 text-muted-foreground'
  return 'border-border bg-background/45 text-muted-foreground'
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
    <div className="rounded-2xl border border-dashed border-border/80 bg-background/30 px-5 py-7 text-sm text-muted-foreground">
      No {label} published yet.
    </div>
  )
}

function LoadingRows({ compact = false }: { compact?: boolean }) {
  return (
    <div className="grid gap-2">
      {Array.from({ length: compact ? 1 : 3 }, (_, index) => (
        <div className="h-16 animate-pulse rounded-2xl border border-border bg-secondary/25" key={index} />
      ))}
    </div>
  )
}

function flattenPages<T extends ContentItem>(query: ReturnType<typeof useModuleContent<T>>) {
  return query.data?.pages.flatMap((page) => page.results) ?? []
}

function nextAdventurePractice(adventure: CommandDrillAdventureSummary | null) {
  if (!adventure) return null
  const levels = adventure.levels.filter((level) => level.next_practice)
  const preferred =
    levels.find((level) => level.next_practice?.status === 'in_progress') ??
    levels.find((level) => level.status !== 'completed' && level.status !== 'locked') ??
    levels.find((level) => level.next_practice?.review_available) ??
    levels[0]
  return preferred?.next_practice ?? null
}

function adventureNextLabel(adventure: CommandDrillAdventureSummary | null) {
  if (!adventure) return null
  const current = adventure.levels.find((level) => level.status === 'in_progress') ??
    adventure.levels.find((level) => level.unlocked && level.status !== 'completed') ??
    adventure.levels.find((level) => level.status !== 'locked')
  if (!current) return null
  return current.next_practice?.title ?? `Level ${current.number}`
}

export function ModulePracticeHub({ module }: { module: LearningModule }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const hubRef = useRef<HTMLDivElement | null>(null)
  const isInView = useInView(hubRef, { amount: 0.15, margin: '420px 0px 420px 0px' })
  const adventureQuery = useModuleContent<CommandDrillAdventureSummary>(module.id, 'command_adventures', isInView)
  const workflowQuery = useModuleContent<WorkflowScenarioSummary>(module.id, 'workflow_scenarios', isInView)

  const adventure = flattenPages(adventureQuery)[0] ?? null
  const workflowScenarios = flattenPages(workflowQuery)
  const adventurePractice = nextAdventurePractice(adventure)
  const nextLabel = adventureNextLabel(adventure)

  const workflowLoadRef = useVisibleLoadMore(
    Boolean(isInView && workflowQuery.hasNextPage && !workflowQuery.isFetchingNextPage),
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
    <div ref={hubRef} className="module-hub-stage grid gap-5">
      <motion.section
        className="command-adventure-card overflow-hidden rounded-[1.65rem] border border-primary/25 bg-card/80 p-5 shadow-[0_24px_70px_rgba(0,0,0,0.28)] backdrop-blur"
        initial={{ opacity: 0, y: 26, rotateX: -6 }}
        whileInView={{ opacity: 1, y: 0, rotateX: 0 }}
        viewport={{ amount: 0.35, once: false, margin: '-8% 0px -8% 0px' }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="flex flex-wrap items-center justify-between gap-5">
          <div className="flex min-w-0 flex-1 items-center gap-4">
            <span className="command-adventure-emblem">
              <TerminalSquare className="size-5" />
            </span>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <p className="text-xs font-black uppercase tracking-[0.2em] text-primary">Command Adventure</p>
                {adventure?.progress.value === 100 ? <CheckCircle2 className="size-4 text-primary" /> : null}
              </div>
              <h3 className="mt-1 text-2xl font-black leading-tight">{adventure?.title ?? 'Loading route'}</h3>
              <p className="mt-1 line-clamp-1 max-w-2xl text-sm text-muted-foreground">
                {adventure?.description ?? 'Preparing command levels.'}
              </p>
            </div>
          </div>

          {adventure ? (
            <div className="command-adventure-progress min-w-[13rem] flex-1 sm:max-w-[18rem]">
              <div className="flex items-center justify-between gap-3 font-mono text-xs text-muted-foreground">
                <span>{nextLabel ? `Next: ${nextLabel}` : 'Progress'}</span>
                <span>{adventure.progress.numerator}/{adventure.progress.denominator}</span>
              </div>
              <ProgressBar value={adventure.progress.value} className="mt-2 h-2.5" glow fillAnimate />
            </div>
          ) : null}

          {adventurePractice ? (
            <PracticeActionButton
              className="h-11 rounded-full px-6"
              disabled={actionPending}
              item={adventurePractice}
              onAction={runPracticeAction}
            />
          ) : adventure && adventure.progress.value >= 100 ? (
            <Button type="button" size="sm" variant="outline" className="h-11 rounded-full px-6" disabled>
              <CheckCircle2 data-icon="inline-start" />
              Complete
            </Button>
          ) : null}
        </div>
        {adventureQuery.isLoading ? <div className="mt-4"><LoadingRows compact /></div> : null}
        {!adventureQuery.isLoading && !adventure ? <div className="mt-4"><EmptySection label="command adventures" /></div> : null}
      </motion.section>

      <motion.section
        className="git-it-challenge-zone rounded-[1.65rem] border border-border/80 bg-background/35 p-5 shadow-[0_18px_56px_rgba(0,0,0,0.2)]"
        initial={{ opacity: 0, y: 28 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ amount: 0.24, once: false, margin: '-8% 0px -8% 0px' }}
        transition={{ duration: 0.52, ease: [0.16, 1, 0.3, 1], delay: 0.05 }}
      >
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded-2xl border border-accent/25 bg-accent/10 text-accent">
              <Swords className="size-5" />
            </span>
            <div>
              <h3 className="text-lg font-black leading-tight">Git it Challenge</h3>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted-foreground">
                {module.workflow_scenario_count} towers
              </p>
            </div>
          </div>
          <div className="hidden items-center gap-2 rounded-full border border-border/70 bg-card/45 px-3 py-1.5 font-mono text-xs text-muted-foreground sm:flex">
            <ChevronsUp className="size-4 text-primary" />
            Easy → Medium → Hard
          </div>
        </div>

        {workflowQuery.isLoading ? <div className="mt-4"><LoadingRows /></div> : null}
        {!workflowQuery.isLoading && workflowScenarios.length === 0 ? <div className="mt-4"><EmptySection label="Git it challenges" /></div> : null}

        <div className="mt-5 grid gap-4 xl:grid-cols-2">
          {workflowScenarios.map((scenario, index) => (
            <ChallengeTowerCard
              disabled={actionPending}
              index={index}
              key={scenario.id}
              scenario={scenario}
              onAction={runPracticeAction}
            />
          ))}
        </div>
        <div ref={workflowLoadRef} />
        {workflowQuery.isFetchingNextPage ? <div className="mt-3"><LoadingRows compact /></div> : null}
        {workflowQuery.hasNextPage ? (
          <Button className="mt-4 rounded-full" type="button" variant="ghost" size="sm" onClick={() => void workflowQuery.fetchNextPage()}>
            More towers
            <ArrowRight data-icon="inline-end" />
          </Button>
        ) : null}
      </motion.section>
    </div>
  )
}

function ChallengeTowerCard({
  scenario,
  disabled,
  index,
  onAction,
}: {
  scenario: WorkflowScenarioSummary
  disabled: boolean
  index: number
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const Icon = CHALLENGE_ICONS[index % CHALLENGE_ICONS.length]
  const completeCount = useMemo(
    () => scenario.levels.filter((level) => level.status === 'completed').length,
    [scenario.levels],
  )
  const overall = scenario.levels.length ? Math.round((completeCount / scenario.levels.length) * 100) : 0

  return (
    <motion.article
      className="challenge-tower-card rounded-[1.35rem] border border-border/75 bg-card/62 p-4 transition hover:border-primary/30 hover:bg-card/75"
      initial={{ opacity: 0, y: 28, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.26, once: false }}
      transition={{ duration: 0.42, delay: index * 0.035, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="flex items-start gap-3">
        <span className="challenge-tower-icon">
          <Icon className="size-5" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="font-mono text-[10px] font-black uppercase tracking-[0.18em] text-primary">Tower {index + 1}</p>
              <h4 className="mt-1 text-lg font-black leading-tight">{scenario.title}</h4>
              <p className="mt-1 line-clamp-1 text-sm text-muted-foreground">{scenario.summary}</p>
            </div>
            <div className="min-w-[6rem] text-right">
              <p className="font-mono text-xs text-muted-foreground">{completeCount}/{scenario.levels.length}</p>
              <ProgressBar value={overall} className="mt-1.5 h-1.5" glow={overall > 0} />
            </div>
          </div>

          {scenario.command_topics.length ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {scenario.command_topics.slice(0, 4).map((topic) => (
                <span className="rounded-full border border-border/70 bg-background/55 px-2 py-1 font-mono text-[10px] text-muted-foreground" key={topic}>
                  {topic}
                </span>
              ))}
            </div>
          ) : null}

          <div className="challenge-tower-floors mt-4 grid gap-2">
            {scenario.levels.map((level, floorIndex) => (
              <ChallengeFloor
                disabled={disabled}
                floorIndex={floorIndex}
                key={level.id}
                level={level}
                onAction={onAction}
              />
            ))}
          </div>
        </div>
      </div>
    </motion.article>
  )
}

function ChallengeFloor({
  level,
  disabled,
  floorIndex,
  onAction,
}: {
  level: WorkflowLevelAccess
  disabled: boolean
  floorIndex: number
  onAction: (item: PracticeAccess, action: PracticeActionIntent) => void
}) {
  const latestAccuracy = level.latest_attempt?.accuracy_rate
  const difficulty = DIFFICULTY_COPY[String(level.difficulty)] ?? {
    label: String(level.difficulty),
    hint: 'Challenge',
  }
  const locked = level.status === 'locked'

  return (
    <div
      className={cn(
        'challenge-floor rounded-2xl border bg-background/40 p-3',
        locked ? 'border-border/45 opacity-60' : 'border-border/80',
      )}
      style={{ animationDelay: `${floorIndex * 50}ms` }}
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className={cn('challenge-floor-dot', locked && 'challenge-floor-dot-locked')}>
            {locked ? <Lock className="size-3.5" /> : <GitCommitHorizontal className="size-3.5" />}
          </span>
          <div>
            <div className="flex items-center gap-2">
              <p className="text-sm font-black">{difficulty.label}</p>
              <StatusPill status={level.status} />
            </div>
            <p className="mt-0.5 flex items-center gap-1 text-xs text-muted-foreground">
              <CircleDotDashed className="size-3" />
              {latestAccuracy !== null && latestAccuracy !== undefined ? `${latestAccuracy}% accuracy` : difficulty.hint}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-3">
          <PracticeProgress item={level} compact />
          <PracticeActionButton className="h-9 rounded-full px-4" disabled={disabled} item={level} onAction={onAction} />
        </div>
      </div>
    </div>
  )
}
