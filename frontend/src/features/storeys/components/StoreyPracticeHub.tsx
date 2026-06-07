import { useEffect, useId, useRef, useState, type CSSProperties } from 'react'
import { useInfiniteQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowRight,
  CheckCircle2,
  Circle,
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

import { challengesApi } from '@/features/challenges/api/challengesApi'
import type {
  ChallengeActionIntent,
  ChallengeLevelAccess,
  ChallengeSummary,
  CommandAdventureSummary,
  StoreyContentPage,
  StoreyContentSection,
} from '@/features/challenges/types'
import type { LearningStorey } from '@/features/storeys/types'
import { syncChallengeRunInCache } from '@/features/challenges/utils/challengeRunCache'
import { meetsMasteryAccuracy, meetsProgressAccuracy } from '@/shared/practice/utils/commandAccuracy'
import { Button } from '@/shared/components/Button'
import { Modal } from '@/shared/components/Modal'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

type ContentItem = CommandAdventureSummary | ChallengeSummary

// Per-difficulty label + accent (RGB triplet consumed via `rgba(var(--level-accent), …)`).
const DIFFICULTY_ACCENT: Record<string, { label: string; rgb: string }> = {
  easy: { label: 'Easy', rgb: '0, 245, 212' },
  medium: { label: 'Medium', rgb: '53, 143, 255' },
  hard: { label: 'Hard', rgb: '176, 74, 255' },
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

function useStoreyContent<T extends ContentItem>(storeyId: number, section: StoreyContentSection, enabled: boolean) {
  return useInfiniteQuery({
    queryKey: queryKeys.storeyContent(storeyId, section),
    queryFn: ({ pageParam }) =>
      challengesApi.storeyContent(storeyId, section, {
        cursor: typeof pageParam === 'number' ? pageParam : null,
        limit: section === 'command_adventures' ? 1 : 6,
      }) as unknown as Promise<StoreyContentPage<T>>,
    initialPageParam: null as number | null,
    getNextPageParam: (lastPage) => lastPage.next_cursor,
    enabled,
    staleTime: 2 * 60 * 1000,
  })
}

function actionForChallengeLevel(item: ChallengeLevelAccess): ChallengeActionIntent | null {
  if (item.status === 'locked') return null
  if (item.status === 'in_progress') return item.active_run_id ? 'resume' : null
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

function actionLabel(action: ChallengeActionIntent | null, status: ChallengeLevelAccess['status']) {
  if (status === 'locked') return 'Locked'
  if (action === 'review') return 'Review'
  if (action === 'continue' || action === 'resume') return 'Continue'
  if (action === 'retry') return 'Retry'
  return 'Start'
}

function ActionIcon({ action, status }: { action: ChallengeActionIntent | null; status: ChallengeLevelAccess['status'] }) {
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

function ChallengeActionButton({
  item,
  disabled,
  className,
  onAction,
}: {
  item: ChallengeLevelAccess
  disabled: boolean
  className?: string
  onAction: (item: ChallengeLevelAccess, action: ChallengeActionIntent) => void
}) {
  const action = actionForChallengeLevel(item)
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

function adventureActionLabel(adventure: CommandAdventureSummary) {
  if (adventure.status === 'completed') return 'Complete'
  if (adventure.active_run_id) return 'Continue'
  if (adventure.latest_run_id) return 'Retry'
  return 'Start'
}

function difficultyLabel(level: ChallengeLevelAccess) {
  return DIFFICULTY_ACCENT[String(level.difficulty)]?.label ?? String(level.difficulty)
}

function LevelStatusIcon({ level }: { level: ChallengeLevelAccess }) {
  if (level.status === 'locked') return <Lock className="size-3.5" />
  if (level.status === 'completed') return <CheckCircle2 className="size-3.5" />
  return <Circle className="size-3.5" />
}

function GargoyleStatueGlyph({ className }: { className?: string }) {
  const uid = useId().replace(/:/g, '')
  const stoneId = `gargoyleStone${uid}`
  const darkStoneId = `gargoyleDarkStone${uid}`
  const chestId = `gargoyleChest${uid}`
  const hornId = `gargoyleHorn${uid}`
  const eyeId = `gargoyleEye${uid}`
  const reliefId = `gargoyleRelief${uid}`

  return (
    <svg className={className} viewBox="0 0 208 190" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id={stoneId} x1="72" y1="38" x2="135" y2="158" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#d9e6f7" />
          <stop offset="0.2" stopColor="#9fb3d6" />
          <stop offset="0.55" stopColor="#596c9c" />
          <stop offset="1" stopColor="#20294e" />
        </linearGradient>
        <linearGradient id={darkStoneId} x1="40" y1="24" x2="160" y2="151" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#a8bad7" />
          <stop offset="0.36" stopColor="#4d5d8a" />
          <stop offset="1" stopColor="#151b38" />
        </linearGradient>
        <linearGradient id={chestId} x1="90" y1="89" x2="119" y2="149" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#e6eef9" />
          <stop offset="0.4" stopColor="#8194be" />
          <stop offset="1" stopColor="#273052" />
        </linearGradient>
        <linearGradient id={hornId} x1="83" y1="20" x2="126" y2="61" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#ecf5ff" />
          <stop offset="0.48" stopColor="#7687ad" />
          <stop offset="1" stopColor="#1b2340" />
        </linearGradient>
        <radialGradient id={eyeId} cx="0" cy="0" r="1" gradientTransform="matrix(18 0 0 12 104 77)" gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="#f6ffff" />
          <stop offset="0.42" stopColor="#8ffdf9" />
          <stop offset="1" stopColor="#b04aff" />
        </radialGradient>
        <filter id={reliefId} x="-18%" y="-18%" width="136%" height="146%">
          <feDropShadow dx="-1.4" dy="-1.2" stdDeviation="0.8" floodColor="#f1f7ff" floodOpacity="0.2" />
          <feDropShadow dx="0" dy="4" stdDeviation="2.1" floodColor="#020617" floodOpacity="0.58" />
        </filter>
      </defs>
      <path className="gargoyle-shadow" d="M45 169 C58 155 78 149 103 149 C130 149 152 156 165 170 C136 184 74 184 45 169 Z" />
      <g className="gargoyle-sculpture" filter={`url(#${reliefId})`}>
        <g className="gargoyle-wing gargoyle-wing-left">
          <path className="gargoyle-stone-dark" fill={`url(#${darkStoneId})`} d="M82 100 C58 92 33 69 25 31 C49 36 68 54 76 78 C82 67 94 61 106 65 C98 76 90 88 82 100 Z" />
          <path className="gargoyle-stone-ridge" d="M36 42 C51 52 63 68 70 91 M54 48 C58 67 66 82 80 98" />
          <path className="gargoyle-underside" d="M32 37 C46 63 62 83 82 100 C61 93 41 73 32 37 Z" />
        </g>
        <g className="gargoyle-wing gargoyle-wing-right">
          <path className="gargoyle-stone-dark" fill={`url(#${darkStoneId})`} d="M126 100 C150 92 175 69 183 31 C159 36 140 54 132 78 C126 67 114 61 102 65 C110 76 118 88 126 100 Z" />
          <path className="gargoyle-stone-ridge" d="M172 42 C157 52 145 68 138 91 M154 48 C150 67 142 82 128 98" />
          <path className="gargoyle-underside" d="M176 37 C162 63 146 83 126 100 C147 93 167 73 176 37 Z" />
        </g>
        <path className="gargoyle-tail" d="M83 139 C58 141 44 132 44 119 C44 109 54 105 61 111 C52 114 53 123 63 126 C72 129 83 125 89 116" />
        <g className="gargoyle-body">
          <path className="gargoyle-stone-fill" fill={`url(#${stoneId})`} d="M74 144 C74 115 81 91 95 80 H113 C127 91 134 115 134 144 C123 154 86 154 74 144 Z" />
          <path className="gargoyle-stone-mid" fill={`url(#${chestId})`} d="M88 143 C89 120 94 100 104 89 C114 100 120 120 120 143 C112 148 96 148 88 143 Z" />
          <path className="gargoyle-core-shadow" d="M76 126 C85 136 96 141 104 141 C114 141 125 136 132 126 V146 C119 155 88 155 74 146 Z" />
          <path className="gargoyle-stone-ridge" d="M92 98 C98 107 101 122 101 141 M116 99 C110 109 107 123 107 141" />
          <path className="gargoyle-bevel" d="M84 115 C90 98 96 88 104 84 C112 88 118 98 124 115" />
        </g>
        <g className="gargoyle-arm gargoyle-arm-left">
          <path className="gargoyle-stone-dark" fill={`url(#${darkStoneId})`} d="M82 102 C62 110 54 124 57 146 C64 145 69 140 70 132 C72 121 78 115 88 112 Z" />
          <path className="gargoyle-claw" d="M57 145 L51 154 M63 145 L61 157 M69 141 L75 151" />
        </g>
        <g className="gargoyle-arm gargoyle-arm-right">
          <path className="gargoyle-stone-dark" fill={`url(#${darkStoneId})`} d="M126 102 C146 110 154 124 151 146 C144 145 139 140 138 132 C136 121 130 115 120 112 Z" />
          <path className="gargoyle-claw" d="M151 145 L157 154 M145 145 L147 157 M139 141 L133 151" />
        </g>
        <g className="gargoyle-head">
          <path className="gargoyle-horn" fill={`url(#${hornId})`} d="M82 57 C74 45 73 33 80 22 C90 33 94 45 91 58" />
          <path className="gargoyle-horn" fill={`url(#${hornId})`} d="M126 57 C134 45 135 33 128 22 C118 33 114 45 117 58" />
          <path className="gargoyle-ear" fill={`url(#${darkStoneId})`} d="M82 73 L61 62 L75 85 Z" />
          <path className="gargoyle-ear" fill={`url(#${darkStoneId})`} d="M126 73 L147 62 L133 85 Z" />
          <path className="gargoyle-stone-fill" fill={`url(#${stoneId})`} d="M76 65 C78 46 92 37 104 37 C116 37 130 46 132 65 C135 90 122 104 104 104 C86 104 73 90 76 65 Z" />
          <path className="gargoyle-face-plane" d="M84 63 C90 51 99 46 104 46 C109 46 119 51 124 63 C121 60 114 59 108 63 C105 65 103 65 100 63 C94 59 87 60 84 63 Z" />
          <path className="gargoyle-brow" d="M86 68 C93 62 100 62 104 68 C108 62 116 62 122 68" />
          <path className="gargoyle-eye" fill={`url(#${eyeId})`} d="M88 76 C93 72 98 72 101 77 C96 80 92 80 88 76 Z" />
          <path className="gargoyle-eye" fill={`url(#${eyeId})`} d="M120 76 C115 72 110 72 107 77 C112 80 116 80 120 76 Z" />
          <path className="gargoyle-nose" d="M104 79 L98 91 H110 Z" />
          <path className="gargoyle-jaw" d="M88 91 C96 102 113 102 121 91 C118 111 91 111 88 91 Z" />
          <path className="gargoyle-tooth" d="M96 96 L99 105 L102 96 M108 96 L111 105 L114 96" />
        </g>
        <path className="gargoyle-crack" d="M118 48 L112 58 L120 65 M88 114 L96 121 L91 133 M132 83 L142 89 M72 82 L62 90" />
        <path className="gargoyle-highlight" d="M90 48 C97 42 108 41 117 47 M84 71 C78 87 85 99 98 105 M124 70 C130 86 123 99 110 105" />
      </g>
    </svg>
  )
}

// A doorway that swings open on hover/focus and opens its modal on click — the
// single interactive entry point that replaces the old start/continue buttons.
function TowerDoor({
  variant,
  caption = 'Enter',
  disabled = false,
  onOpen,
  ariaLabel,
}: {
  variant: 'challenge' | 'adventure'
  caption?: string
  disabled?: boolean
  onOpen: () => void
  ariaLabel: string
}) {
  return (
    <button
      type="button"
      className="tower-door"
      data-variant={variant}
      disabled={disabled}
      onClick={onOpen}
      aria-label={ariaLabel}
    >
      <span className="tower-door-arch" aria-hidden="true">
        <span className="tower-door-interior">
          <span className="tower-door-light" />
        </span>
        <span className="tower-door-leaf">
          <span className="tower-door-plank tower-door-plank--left" />
          <span className="tower-door-plank tower-door-plank--right" />
          <span className="tower-door-brace tower-door-brace--top" />
          <span className="tower-door-brace tower-door-brace--bottom" />
          <span className="tower-door-handle" />
        </span>
        <span className="tower-door-frame" />
        <span className="tower-door-threshold" />
      </span>
      <span className="tower-door-caption">{caption}</span>
    </button>
  )
}

function AdventureModal({
  open,
  adventure,
  pending,
  onClose,
  onAction,
}: {
  open: boolean
  adventure: CommandAdventureSummary
  pending: boolean
  onClose: () => void
  onAction: () => void
}) {
  const completed = adventure.status === 'completed'

  return (
    <Modal
      open={open}
      title={adventure.title}
      className="w-full max-w-lg overflow-hidden border-[rgba(45,245,255,0.4)] bg-card shadow-[0_24px_100px_rgba(45,245,255,0.18)]"
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="adventure-modal-body">
        <span className="adventure-modal-icon">
          <Swords className="size-7" />
        </span>
        <p className="adventure-modal-copy">
          {adventure.description?.trim()
            ? adventure.description
            : 'Master Git command forms through hands-on practice across this storey.'}
        </p>

        <div className="adventure-modal-progress">
          <div className="adventure-modal-progress-meta">
            <span>
              {adventure.progress.numerator}/{adventure.progress.denominator} solved
            </span>
            <span>{adventure.progress.value}%</span>
          </div>
          <ProgressBar value={adventure.progress.value} className="h-3 bg-secondary/60" glow fillAnimate />
        </div>

        <Button
          type="button"
          className="adventure-modal-action"
          variant={completed ? 'outline' : 'default'}
          disabled={pending || completed}
          onClick={onAction}
        >
          {completed ? <CheckCircle2 data-icon="inline-start" /> : <Play data-icon="inline-start" />}
          {adventureActionLabel(adventure)}
        </Button>
      </div>
    </Modal>
  )
}

function LevelCard({
  level,
  index,
  disabled,
  onAction,
}: {
  level: ChallengeLevelAccess
  index: number
  disabled: boolean
  onAction: (item: ChallengeLevelAccess, action: ChallengeActionIntent) => void
}) {
  const accent = DIFFICULTY_ACCENT[String(level.difficulty)]?.rgb ?? '176, 74, 255'
  const locked = level.status === 'locked'
  const completed = level.status === 'completed'
  const required = level.successful_attempts.required
  const cleared = level.successful_attempts.count
  const progressPct = required > 0 ? Math.min(100, Math.round((cleared / required) * 100)) : 0
  const accuracy = level.latest_attempt?.accuracy_rate

  return (
    <li
      className={cn('level-card', locked && 'is-locked', completed && 'is-complete')}
      style={{ '--level-accent': accent, animationDelay: `${index * 70}ms` } as CSSProperties}
    >
      <span className="level-card-rank">{index + 1}</span>
      <div className="level-card-main">
        <div className="level-card-head">
          <span className="level-card-name">{difficultyLabel(level)}</span>
          <span className="level-card-status">
            <LevelStatusIcon level={level} />
          </span>
        </div>
        <div className="level-card-meta">
          <span>
            {cleared}/{required} cleared
          </span>
          {accuracy !== null && accuracy !== undefined ? (
            <span className="level-card-accuracy">{accuracy}% accuracy</span>
          ) : null}
        </div>
        <ProgressBar value={progressPct} className="mt-2 h-1.5 bg-secondary/55" />
      </div>
      <ChallengeActionButton
        className="level-card-action"
        disabled={disabled}
        item={level}
        onAction={onAction}
      />
    </li>
  )
}

function ChallengeLevelsModal({
  open,
  scenario,
  disabled,
  onClose,
  onAction,
}: {
  open: boolean
  scenario: ChallengeSummary
  disabled: boolean
  onClose: () => void
  onAction: (item: ChallengeLevelAccess, action: ChallengeActionIntent) => void
}) {
  return (
    <Modal
      open={open}
      title={scenario.title}
      className="w-full max-w-lg overflow-hidden border-[rgba(176,74,255,0.45)] bg-card shadow-[0_24px_100px_rgba(176,74,255,0.22)]"
      contentClassName="p-0"
      onClose={onClose}
    >
      <div className="challenge-levels-body">
        {scenario.summary?.trim() ? <p className="challenge-levels-summary">{scenario.summary}</p> : null}

        {scenario.command_topics.length ? (
          <div className="challenge-levels-topics">
            {scenario.command_topics.map((topic) => (
              <span className="challenge-levels-topic" key={topic}>
                {topic}
              </span>
            ))}
          </div>
        ) : null}

        <ul className="challenge-levels-list">
          {scenario.levels.map((level, index) => (
            <LevelCard
              disabled={disabled}
              index={index}
              key={level.id}
              level={level}
              onAction={onAction}
            />
          ))}
        </ul>
      </div>
    </Modal>
  )
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
  const levels = storey.challenge_count * 3

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
          <OverviewStat icon={ListChecks} label="Command skills" value={storey.command_skill_count} />
          <OverviewStat icon={Swords} label="GIT Challenged" value={storey.challenge_count} />
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
  const [adventureModalOpen, setAdventureModalOpen] = useState(false)
  // Kick the per-storey fetch off well before the storey scrolls into view, then
  // latch it on so the content stays loaded (no refetch thrash on scroll in/out).
  const nearViewport = useInView(hubRef, { margin: '1100px 0px 1100px 0px' })
  const [shouldLoad, setShouldLoad] = useState(false)
  useEffect(() => {
    if (!nearViewport || shouldLoad) return
    const frame = window.requestAnimationFrame(() => setShouldLoad(true))
    return () => window.cancelAnimationFrame(frame)
  }, [nearViewport, shouldLoad])

  const adventureQuery = useStoreyContent<CommandAdventureSummary>(storey.id, 'command_adventures', shouldLoad)
  const workflowQuery = useStoreyContent<ChallengeSummary>(storey.id, 'challenges', shouldLoad)

  const adventure = flattenPages(adventureQuery)[0] ?? null
  const workflowScenarios = flattenPages(workflowQuery)

  const workflowLoadRef = useVisibleLoadMore(
    Boolean(shouldLoad && workflowQuery.hasNextPage && !workflowQuery.isFetchingNextPage),
    () => void workflowQuery.fetchNextPage(),
  )

  const startMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })
  const reviewMutation = useMutation({
    mutationFn: (levelId: number) => challengesApi.startChallengeRun(levelId, { review: true }),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })
  const retryMutation = useMutation({
    mutationFn: (runId: number) => challengesApi.retryChallengeRun(runId),
    onSuccess: (run) => {
      syncChallengeRunInCache(queryClient, run)
      navigate(`/challenge-runs/${run.id}`)
    },
  })

  function runChallengeAction(item: ChallengeLevelAccess, action: ChallengeActionIntent) {
    if (action === 'resume' && item.active_run_id) {
      navigate(`/challenge-runs/${item.active_run_id}`)
      return
    }
    if (action === 'review') {
      reviewMutation.mutate(item.id)
      return
    }
    if (action === 'retry' && item.latest_attempt?.id) {
      retryMutation.mutate(item.latest_attempt.id)
      return
    }
    startMutation.mutate(item.id)
  }

  function runAdventureAction(adventure: CommandAdventureSummary) {
    if (adventure.active_run_id) {
      navigate(`/adventure-runs/${adventure.active_run_id}`)
      return
    }
    navigate(`/command-adventures/${adventure.slug}`)
  }

  const actionPending = startMutation.isPending || reviewMutation.isPending || retryMutation.isPending
  // GIT Challenged stays chained shut until the storey's Command Adventure is cleared.
  const challengesLocked = adventure !== null && adventure.status !== 'completed'
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
          <div className="tower-peak" aria-hidden="true">
            <div className="tower-flag-wrap">
              <span className="tower-flag-pole" />
              <span className="tower-flag" />
            </div>
            <div className="tower-peak-roof" />
            <div className="tower-crown">
              <span />
              <span />
              <span />
            </div>
          </div>
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

            {adventureQuery.isLoading ? <LoadingRows compact /> : null}
            {!adventureQuery.isLoading && !adventure ? <EmptySection label="Command Adventures" /> : null}

            {adventure ? (
              <div className="tower-door-mount">
                <TowerDoor
                  variant="adventure"
                  ariaLabel={`Open ${adventure.title}`}
                  disabled={actionPending}
                  onOpen={() => setAdventureModalOpen(true)}
                />
              </div>
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
            className={cn('tower-floor challenge-floor-zone', challengesLocked && 'is-locked')}
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
                  disabled={actionPending || challengesLocked}
                  index={index}
                  key={scenario.id}
                  locked={challengesLocked}
                  scenario={scenario}
                  onAction={runChallengeAction}
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

        {isLast ? (
          <div className="tower-base" aria-hidden="true">
            <span className="tower-base-foot" />
          </div>
        ) : (
          <div className="tower-stack-connector" aria-hidden="true" />
        )}
      </div>

      {adventure ? (
        <AdventureModal
          open={adventureModalOpen}
          adventure={adventure}
          pending={actionPending}
          onClose={() => setAdventureModalOpen(false)}
          onAction={() => {
            runAdventureAction(adventure)
            setAdventureModalOpen(false)
          }}
        />
      ) : null}
    </section>
  )
}

function ChallengeRoom({
  scenario,
  disabled,
  index,
  locked,
  onAction,
}: {
  scenario: ChallengeSummary
  disabled: boolean
  index: number
  locked: boolean
  onAction: (item: ChallengeLevelAccess, action: ChallengeActionIntent) => void
}) {
  const [open, setOpen] = useState(false)
  const completed = scenario.levels.length > 0 && scenario.levels.every((level) => level.status === 'completed')
  const inProgress = scenario.levels.some((level) => level.status === 'in_progress')
  const statueState = locked ? 'locked' : completed ? 'completed' : inProgress ? 'in-progress' : 'available'

  return (
    <>
      <motion.article
        className="challenge-room"
        initial={{ opacity: 0, y: 18, scale: 0.99 }}
        whileInView={{ opacity: 1, y: 0, scale: 1 }}
        viewport={{ amount: 0.24, once: true }}
        transition={{ duration: 0.44, delay: index * 0.025, ease: [0.16, 1, 0.3, 1] }}
      >
        <button
          type="button"
          className="challenge-gargoyle"
          data-state={statueState}
          disabled={disabled}
          onClick={() => setOpen(true)}
          aria-label={`Open ${scenario.title}`}
        >
          <span className="challenge-gargoyle-figure" aria-hidden="true">
            <span className="challenge-gargoyle-aura" />
            <GargoyleStatueGlyph className="challenge-gargoyle-art" />
          </span>
          <span className="challenge-gargoyle-plinth">
            <span className="challenge-room-index">Trial {index + 1}</span>
            <h3 className="challenge-room-title">{scenario.title}</h3>
          </span>
        </button>
      </motion.article>

      <ChallengeLevelsModal
        open={open}
        scenario={scenario}
        disabled={disabled}
        onClose={() => setOpen(false)}
        onAction={(item, action) => {
          onAction(item, action)
          setOpen(false)
        }}
      />
    </>
  )
}
