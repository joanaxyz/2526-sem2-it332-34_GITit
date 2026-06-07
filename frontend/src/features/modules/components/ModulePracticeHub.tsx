import { useEffect, useRef } from 'react'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  CheckCircle2,
  Circle,
  Flag,
  Gem,
  Layers3,
  ListChecks,
  Lock,
  Play,
  RefreshCcw,
  RotateCcw,
  Swords,
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
  TowerContentPage,
  TowerContentSection,
  PracticeAccess,
  PracticeActionIntent,
  WorkflowLevelAccess,
  WorkflowScenarioSummary,
} from '@/features/scenarios/types'
import type { LearningStorey } from '@/features/modules/types'
import { syncPracticeSessionInCache } from '@/features/practice/utils/practiceCache'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/features/practice/utils/commandAccuracy'
import { Button } from '@/shared/components/Button'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

type ContentItem = CommandDrillAdventureSummary | CommandTopicSummary | WorkflowScenarioSummary

const CHALLENGE_ICONS: LucideIcon[] = [Flag, Swords, Trophy]
const DIFFICULTY_COPY: Record<string, { label: string }> = {
  easy: { label: 'Easy' },
  medium: { label: 'Medium' },
  hard: { label: 'Hard' },
}
const REWARD_MARKERS = [
  { value: 25, label: '+25 XP' },
  { value: 50, label: '+60 XP' },
  { value: 75, label: '+100 XP' },
  { value: 100, label: 'Crown chest' },
]

function nextReward(progress: number) {
  return REWARD_MARKERS.find((marker) => progress < marker.value) ?? REWARD_MARKERS[REWARD_MARKERS.length - 1]
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

function useStoreyContent<T extends ContentItem>(storeyId: number, section: TowerContentSection, enabled: boolean) {
  return useInfiniteQuery({
    queryKey: queryKeys.storeyContent(storeyId, section),
    queryFn: ({ pageParam }) =>
      scenariosApi.storeyContent(storeyId, section, {
        cursor: typeof pageParam === 'number' ? pageParam : null,
        limit: section === 'command_adventures' ? 1 : 6,
      }) as unknown as Promise<TowerContentPage<T>>,
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

function EmptySection({ label }: { label: string }) {
  return (
    <div className="tower-empty-state">
      No {label} published yet.
    </div>
  )
}

function LoadingRows({ compact = false }: { compact?: boolean }) {
  return (
    <div className="tower-loading-stack">
      {Array.from({ length: compact ? 1 : 3 }, (_, index) => (
        <div className="tower-loading-row" key={index} />
      ))}
    </div>
  )
}

function flattenPages<T extends ContentItem>(query: ReturnType<typeof useStoreyContent<T>>) {
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

function difficultyLabel(level: WorkflowLevelAccess) {
  return DIFFICULTY_COPY[String(level.difficulty)]?.label ?? String(level.difficulty)
}

function LevelStatusIcon({ level }: { level: WorkflowLevelAccess }) {
  if (level.status === 'locked') return <Lock className="size-3.5" />
  if (level.status === 'completed') return <CheckCircle2 className="size-3.5" />
  return <Circle className="size-3.5" />
}

function OverviewStat({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon
  label: string
  value: string | number
}) {
  return (
    <div className="tower-overview-stat">
      <span className="tower-overview-stat-icon">
        <Icon className="size-4" />
      </span>
      <span className="text-sm text-muted-foreground">{label}</span>
      <strong className="ml-auto text-sm text-foreground">{value}</strong>
    </div>
  )
}

type StoreyPracticeHubProps = {
  storey: LearningStorey
  displayTitle?: string
  isFirst?: boolean
  isLast?: boolean
  sequenceIndex?: number
}

function StoreyOverview({
  storey,
  title,
  progress,
}: {
  storey: LearningStorey
  title: string
  progress: number
}) {
  const reward = nextReward(progress)
  const levels = storey.workflow_scenario_count * 3

  return (
    <motion.aside
      className="storey-overview"
      initial={{ opacity: 0, x: -16 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ amount: 0.28, once: true, margin: '-4% 0px -4% 0px' }}
      transition={{ duration: 0.48, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="storey-overview-heading">
        <div className="tower-heading-row">
          <h2 className="storey-overview-title">{title}</h2>
        </div>
        <p className="mt-4 max-w-xs text-base leading-7 text-muted-foreground">
          Storey overview for this Command Adventure and GIT Challenged set.
        </p>
      </div>

      <section className="tower-side-panel storey-overview-card" aria-label={`${title} storey overview`}>
        <div className="grid gap-4">
          <OverviewStat icon={ListChecks} label="Commands to learn" value={storey.command_topic_count} />
          <OverviewStat icon={Swords} label="GIT Challenged" value={storey.workflow_scenario_count} />
          <OverviewStat icon={Layers3} label="Total levels" value={levels} />
        </div>
        <div className="tower-progress-block">
          <div className="flex items-center justify-between gap-3">
            <span className="text-sm text-muted-foreground">Storey Progress</span>
            <strong className="font-mono text-sm text-foreground">{progress}%</strong>
          </div>
          <div className="tower-reward-rail">
            <ProgressBar value={progress} className="h-3 bg-secondary/70" glow fillAnimate />
            <div className="tower-reward-markers" aria-hidden="true">
              {REWARD_MARKERS.map((marker) => (
                <span
                  className={marker.value <= progress ? 'is-earned' : undefined}
                  key={marker.value}
                  style={{ left: `${marker.value}%` }}
                >
                  <img src="/stage_reward_neon_chest.png" alt="" />
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="stage-reward-panel" aria-label={`${title} progress reward`}>
        <div>
          <p className="text-sm text-muted-foreground">Progress Reward</p>
          <p className="mt-2 text-sm font-semibold text-foreground">Next chest at {reward.value}% storey progress</p>
          <p className="mt-3 inline-flex items-center gap-1.5 text-2xl font-black text-foreground">
            {reward.label} <Gem className="size-5 text-warning" />
          </p>
        </div>
        <span className="stage-reward-icon">
          <img className="stage-reward-chest" src="/stage_reward_neon_chest.png" alt="" aria-hidden="true" />
        </span>
      </section>

    </motion.aside>
  )
}

export function StoreyPracticeHub({
  storey,
  displayTitle,
  isFirst = true,
  isLast = true,
  sequenceIndex = 0,
}: StoreyPracticeHubProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const hubRef = useRef<HTMLElement | null>(null)
  const isInView = useInView(hubRef, { amount: 0.15, margin: '420px 0px 420px 0px' })
  const adventureQuery = useStoreyContent<CommandDrillAdventureSummary>(storey.id, 'command_adventures', isInView)
  const workflowQuery = useStoreyContent<WorkflowScenarioSummary>(storey.id, 'workflow_scenarios', isInView)

  const adventure = flattenPages(adventureQuery)[0] ?? null
  const workflowScenarios = flattenPages(workflowQuery)
  const adventurePractice = nextAdventurePractice(adventure)

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
    const payload = startPayloadForPractice(item.practice_kind, item.id, action === 'review' ? 'review' : 'tower_page')
    if (action === 'review') {
      reviewMutation.mutate(payload)
      return
    }
    startMutation.mutate(payload)
  }

  const actionPending = startMutation.isPending || reviewMutation.isPending
  const title = displayTitle ?? storey.title
  const progress = storey.practice_completion?.value ?? 0
  const motionDelay = Math.min(sequenceIndex * 0.03, 0.12)

  return (
    <section
      ref={hubRef}
      className="storey-section"
      aria-label={`${title} storey`}
      data-storey-id={storey.id}
    >
      <StoreyOverview storey={storey} title={title} progress={progress} />

      <div
        className={cn('learning-tower', !isFirst && 'learning-tower-continuation', !isLast && 'learning-tower-continues')}
      >
        {isFirst ? (
          <>
            <div className="tower-flag-wrap" aria-hidden="true">
              <span className="tower-flag-pole" />
              <span className="tower-flag" />
            </div>

            <div className="tower-cap" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
          </>
        ) : null}

        <motion.div
          className="tower-shell"
          initial={{ opacity: 0, y: 22, scale: 0.99 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ amount: 0.18, once: true, margin: '-6% 0px -6% 0px' }}
          transition={{ duration: 0.68, delay: motionDelay, ease: [0.16, 1, 0.3, 1] }}
        >
          <motion.section
            className="tower-floor adventure-floor"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.42, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.03, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-floor-icon">
              <Swords className="size-7" />
            </span>
            <h2 className="tower-floor-title command-adventure-title">Command Adventure</h2>
            <p className="tower-floor-copy">Master Git command forms through hands-on practice.</p>

            {adventure ? (
              <div className="adventure-progress">
                <div className="adventure-progress-meta">
                  <span>{adventure.progress.numerator}/{adventure.progress.denominator}</span>
                  <span>{adventure.progress.value}%</span>
                </div>
                <ProgressBar value={adventure.progress.value} className="h-2.5 bg-secondary/65" glow fillAnimate />
              </div>
            ) : null}

            {adventureQuery.isLoading ? <LoadingRows compact /> : null}
            {!adventureQuery.isLoading && !adventure ? <EmptySection label="Command Adventures" /> : null}

            {adventurePractice ? (
              <PracticeActionButton
                className="tower-action-button h-10 rounded-full border border-primary/55 bg-primary/10 px-5 text-primary shadow-[0_0_22px_rgba(0,245,212,0.16)] hover:bg-primary/15 hover:text-primary"
                disabled={actionPending}
                item={adventurePractice}
                onAction={runPracticeAction}
              />
            ) : adventure && adventure.progress.value >= 100 ? (
              <Button type="button" size="sm" variant="outline" className="tower-action-button h-10 rounded-full px-5" disabled>
                <CheckCircle2 data-icon="inline-start" />
                Complete
              </Button>
            ) : null}
          </motion.section>

          <motion.div
            className="tower-divider"
            aria-hidden="true"
            initial={{ opacity: 0, scaleX: 0.52 }}
            whileInView={{ opacity: 1, scaleX: 1 }}
            viewport={{ amount: 0.6, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.06, ease: [0.16, 1, 0.3, 1] }}
          >
            <span />
          </motion.div>

          <motion.section
            className="tower-floor challenge-floor-zone"
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.16, once: true, margin: '-6% 0px -6% 0px' }}
            transition={{ duration: 0.58, delay: motionDelay + 0.08, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-floor-icon challenge-icon">
              <Trophy className="size-7" />
            </span>
            <h2 className="tower-floor-title challenge-title">GIT Challenged</h2>
            <p className="tower-floor-copy">Apply your skills in scenario challenges.</p>

            {workflowQuery.isLoading ? <div className="mt-5"><LoadingRows /></div> : null}
            {!workflowQuery.isLoading && workflowScenarios.length === 0 ? (
              <div className="mt-5">
                <EmptySection label="GIT Challenged" />
              </div>
            ) : null}

            <div className="challenge-room-stack">
              {workflowScenarios.map((scenario, index) => (
                <ChallengeRoom
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
              <Button
                className="mt-4 h-9 rounded-full px-4"
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => void workflowQuery.fetchNextPage()}
              >
                More GIT Challenged
                <ArrowRight data-icon="inline-end" />
              </Button>
            ) : null}
          </motion.section>
        </motion.div>

        {isLast ? <div className="tower-base" aria-hidden="true" /> : <div className="tower-stack-connector" aria-hidden="true" />}
      </div>
    </section>
  )
}

export const ModulePracticeHub = StoreyPracticeHub

function ChallengeRoom({
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

  return (
    <motion.article
      className="challenge-room"
      initial={{ opacity: 0, y: 18, scale: 0.99 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.24, once: true }}
      transition={{ duration: 0.44, delay: index * 0.025, ease: [0.16, 1, 0.3, 1] }}
    >
      <span className="challenge-room-badge" aria-hidden="true">
        <Icon className="size-4" />
      </span>
      <div className="challenge-room-door" aria-hidden="true" />
      <div className="challenge-room-content">
        <p className="challenge-room-label">Challenge {index + 1}</p>
        <h3 className="challenge-room-title">{scenario.title}</h3>
        <div className="difficulty-row-stack">
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
  const locked = level.status === 'locked'
  const completed = level.status === 'completed'

  return (
    <div
      className={cn('difficulty-row', locked && 'is-locked', completed && 'is-complete')}
      style={{ animationDelay: `${floorIndex * 50}ms` }}
    >
      <span className="difficulty-status" aria-hidden="true">
        <LevelStatusIcon level={level} />
      </span>
      <span className="difficulty-name">{difficultyLabel(level)}</span>
      {latestAccuracy !== null && latestAccuracy !== undefined ? (
        <span className="difficulty-accuracy">{latestAccuracy}%</span>
      ) : null}
      <PracticeActionButton
        className="difficulty-action h-8 rounded-md px-3"
        disabled={disabled}
        item={level}
        onAction={onAction}
      />
    </div>
  )
}
