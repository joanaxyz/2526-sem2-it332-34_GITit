import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import {
  ArrowRight,
  Gem,
  Layers3,
  ListChecks,
  Swords,
  Trophy,
  type LucideIcon,
} from 'lucide-react'
import { motion, useInView } from 'motion/react'

import { challengesApi } from '@/features/challenges/api/challengesApi'
import type {
  ChallengeLevelAccess,
  ChallengeSummary,
  CommandAdventureSummary,
  StoreyContentPage,
  StoreyContentSection,
} from '@/features/challenges/types'
import type { LearningStorey } from '@/features/storeys/types'
import {
  actionForChallengeLevel,
  actionLabel,
  DIFFICULTY_ACCENT,
  difficultyLabel,
  nextReward,
  REWARD_MARKERS,
} from '@/features/storeys/challengeUi'
import { isSelected, useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'
import { Button } from '@/shared/components/Button'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

type ContentItem = CommandAdventureSummary | ChallengeSummary

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

function EmptySection({ label }: { label: string }) {
  return <div className="tower-empty-state">No {label} published yet.</div>
}

// Loading placeholders shaped like the doors they will become, so the tower
// visibly assembles piece by piece instead of flashing generic rows.
function AdventureDoorSkeleton() {
  return (
    <div className="tower-adventure-door-wrap" aria-hidden="true">
      <span className="tower-door-skeleton tower-door-skeleton--gate" />
    </div>
  )
}

function TrialRoomSkeleton() {
  return (
    <div className="tower-door-skeleton-row" aria-hidden="true">
      {Array.from({ length: 3 }, (_, index) => (
        <span
          className="tower-door-skeleton tower-door-skeleton--trial"
          key={index}
          style={{ '--skeleton-index': index } as CSSProperties}
        />
      ))}
    </div>
  )
}

function flattenPages<T extends ContentItem>(query: ReturnType<typeof useStoreyContent<T>>) {
  return query.data?.pages.flatMap((page) => page.results) ?? []
}

const PIECE_EASE = [0.16, 1, 0.3, 1] as const

// ── Windows storey: the lit-window band that tops every storey; the conical roof
// only crowns the very first storey (the top of the whole tower). ──
function WindowStorey({ crowned }: { crowned: boolean }) {
  return (
    <motion.div
      className="tower-window-stage"
      aria-hidden="true"
      initial={{ opacity: 0, y: -22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.55, ease: PIECE_EASE }}
    >
      {crowned ? (
        <div className="tower-window-roof">
          <span className="tower-window-roof-spire" />
          <span className="tower-window-roof-peak" />
        </div>
      ) : null}
      <div className="tower-window-storey">
        <span className="tower-window-storey-window" />
        <span className="tower-window-storey-window" />
        <span className="tower-window-storey-window" />
      </div>
    </motion.div>
  )
}

// Section belt between tower rooms. Challenge-after belts get physical crenels that keep their side outlines closed.
function TowerSectionSeparator({
  continuation = false,
  base = false,
  afterChallenges = false,
}: {
  continuation?: boolean
  base?: boolean
  afterChallenges?: boolean
}) {
  return (
    <motion.div
      className={cn(
        'tower-section-separator',
        continuation && 'is-continuation',
        base && 'is-base',
        afterChallenges && 'is-after-challenges',
      )}
      aria-hidden="true"
      initial={{ opacity: 0, scaleX: 0.86 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      viewport={{ amount: 0.4, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      {afterChallenges ? (
        <span className="tower-section-separator-crenels">
          {Array.from({ length: 9 }, (_, index) => (
            <span key={index} />
          ))}
        </span>
      ) : null}
      <span className="tower-section-separator-backplate" />
    </motion.div>
  )
}

// ── Command Adventure: a single arched neon gate, selectable. The gate
// materializes out of the wall when it scrolls into view. ──
function AdventureDoor({
  adventure,
  selected,
  onSelect,
}: {
  adventure: CommandAdventureSummary
  selected: boolean
  onSelect: () => void
}) {
  return (
    <motion.button
      type="button"
      className="adventure-door"
      data-selected={selected ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select Command Adventure: ${adventure.title}`}
      onClick={onSelect}
      initial={{ opacity: 0, y: 26, scale: 0.9, rotateX: -18, transformPerspective: 760 }}
      whileInView={{ opacity: 1, y: 0, scale: 1, rotateX: 0, transformPerspective: 760 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.62, ease: PIECE_EASE }}
    >
      <span className="adventure-door-frame" aria-hidden="true">
        <span className="adventure-door-interior" />
        <span className="adventure-door-leaf adventure-door-leaf--left">
          <span className="adventure-door-plank" />
        </span>
        <span className="adventure-door-leaf adventure-door-leaf--right">
          <span className="adventure-door-plank" />
        </span>
        <span className="adventure-door-gem" />
      </span>
    </motion.button>
  )
}

// Door reveal choreography: the row staggers its doors one by one; each door
// rises out of the floor, then its portcullis bars drop in sequence. The bars
// keep `x: '-50%'` in both poses because the CSS centring translate would
// otherwise be clobbered by the motion transform.
const trialDoorRowVariants = {
  hidden: {},
  shown: { transition: { staggerChildren: 0.14, delayChildren: 0.05 } },
}

const trialDoorVariants = {
  hidden: { opacity: 0, y: 30, scale: 0.94, rotateX: -22, transformPerspective: 640 },
  shown: {
    opacity: 1,
    y: 0,
    scale: 1,
    rotateX: 0,
    transformPerspective: 640,
    transition: { duration: 0.55, ease: PIECE_EASE, staggerChildren: 0.07, delayChildren: 0.16 },
  },
}

const trialDoorBarVariants = {
  hidden: { x: '-50%', scaleY: 0, originY: 0 },
  shown: { x: '-50%', scaleY: 1, originY: 0, transition: { duration: 0.34, ease: PIECE_EASE } },
}

// ── A single GIT Challenged level door — selectable, framed by difficulty colour. ──
function TrialDoor({
  scenario,
  scenarioIndex,
  level,
  storeyId,
  locked,
}: {
  scenario: ChallengeSummary
  scenarioIndex: number
  level: ChallengeLevelAccess
  storeyId: number
  locked: boolean
}) {
  const select = useTowerSelection((state) => state.select)
  const selected = useTowerSelection((state) =>
    isSelected(state.selected, { kind: 'challenge', storeyId, scenarioIndex, scenario, level, locked }),
  )
  const difficulty = String(level.difficulty)
  const accent = DIFFICULTY_ACCENT[difficulty]?.rgb ?? DIFFICULTY_ACCENT.hard.rgb
  const isLocked = locked || level.status === 'locked'
  const completed = level.status === 'completed'
  const inProgress = level.status === 'in_progress'

  return (
    <motion.button
      type="button"
      className={cn('trial-door', isLocked && 'is-locked', completed && 'is-complete', inProgress && 'is-active')}
      style={{ '--level-accent': accent, '--door-accent': accent } as CSSProperties}
      data-difficulty={difficulty}
      data-selected={selected ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select ${scenario.title}: ${difficultyLabel(level)}`}
      onClick={() => select({ kind: 'challenge', storeyId, scenarioIndex, scenario, level, locked })}
      variants={trialDoorVariants}
    >
      <span className="trial-door-arch" aria-hidden="true">
        <span className="trial-door-interior" />
        <span className="trial-door-gate">
          <span className="trial-door-bars">
            {Array.from({ length: 4 }, (_, index) => (
              <motion.span className="trial-door-bar" key={index} variants={trialDoorBarVariants} />
            ))}
          </span>
          <span className="trial-door-crossbar" />
        </span>
      </span>
      <span className="trial-door-label">{difficultyLabel(level)}</span>
      <span className="trial-door-state">{actionLabel(actionForChallengeLevel(level), level.status)}</span>
    </motion.button>
  )
}

function ChallengeTrial({
  scenario,
  index,
  storeyId,
  locked,
}: {
  scenario: ChallengeSummary
  index: number
  storeyId: number
  locked: boolean
}) {
  return (
    <motion.article
      className="trial-room"
      initial={{ opacity: 0, y: 18, scale: 0.99 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.24, once: true }}
      transition={{ duration: 0.44, delay: index * 0.025, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="trial-room-header">
        <span className="trial-room-kicker">Trial {index + 1}</span>
        <h3 className="trial-room-title">{scenario.title}</h3>
      </div>
      {scenario.summary?.trim() ? <p className="trial-room-summary">{scenario.summary}</p> : null}
      <motion.div
        className="trial-door-row"
        initial="hidden"
        whileInView="shown"
        viewport={{ amount: 0.3, once: true }}
        variants={trialDoorRowVariants}
      >
        {scenario.levels.map((level) => (
          <TrialDoor
            key={level.id}
            scenario={scenario}
            scenarioIndex={index}
            level={level}
            storeyId={storeyId}
            locked={locked}
          />
        ))}
      </motion.div>
    </motion.article>
  )
}

function OverviewStat({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string | number }) {
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

export function StoreyOverview({
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
        <span className="storey-overview-kicker">Storey {storey.number}</span>
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

type StoreyPracticeHubProps = {
  storey: LearningStorey
  displayTitle?: string
  isFirst?: boolean
  isLast?: boolean
  sequenceIndex?: number
}

export function StoreyPracticeHub({
  storey,
  displayTitle,
  isFirst = true,
  isLast = true,
  sequenceIndex = 0,
}: StoreyPracticeHubProps) {
  const hubRef = useRef<HTMLElement | null>(null)
  // Storeys only mount when scrolled to, so a short prefetch margin is enough:
  // content starts loading just before the storey enters the viewport.
  const nearViewport = useInView(hubRef, { margin: '600px 0px 600px 0px' })
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

  const select = useTowerSelection((state) => state.select)
  const selectedAdventureId = useTowerSelection((state) =>
    state.selected?.kind === 'adventure' ? state.selected.adventure.id : null,
  )

  // Gate on the stable "ever passed" flag, not the latest run status: a player
  // who passed once then replays-and-abandons must not see challenges relock
  // (the backend unlock keys off passed_at, so the UI must agree).
  const challengesLocked = adventure !== null && !adventure.is_passed
  const title = displayTitle ?? storey.title
  const motionDelay = Math.min(sequenceIndex * 0.03, 0.12)
  const adventureSelected = adventure !== null && selectedAdventureId === adventure.id

  return (
    <section
      ref={hubRef}
      className="storey-section"
      aria-label={`${title} storey`}
      data-storey-id={storey.id}
    >
      <div className={cn('learning-tower', !isFirst && 'learning-tower-continuation')}>
        {/* Each tower piece (window band, stages, separators, doors) owns its
            entrance animation, so the storey assembles piece by piece. */}
        <div className="tower-repeater">
          <WindowStorey crowned={isFirst} />

          <motion.section
            className="tower-adventure-stage"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.42, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.03, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-stage-icon tower-stage-icon--cyan">
              <Swords className="size-6" />
            </span>
            <h2 className="tower-stage-title tower-stage-title--adventure">Command Adventure</h2>

            {adventureQuery.isLoading ? <AdventureDoorSkeleton /> : null}
            {!adventureQuery.isLoading && !adventure ? <EmptySection label="Command Adventures" /> : null}

            {adventure ? (
              <div className="tower-adventure-door-wrap">
                <AdventureDoor
                  adventure={adventure}
                  selected={adventureSelected}
                  onSelect={() => select({ kind: 'adventure', storeyId: storey.id, adventure })}
                />
              </div>
            ) : null}
          </motion.section>

          <TowerSectionSeparator />

          <motion.section
            className={cn('tower-challenges-stage', challengesLocked && 'is-locked')}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.16, once: true, margin: '-6% 0px -6% 0px' }}
            transition={{ duration: 0.58, delay: motionDelay + 0.08, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-stage-icon tower-stage-icon--purple">
              <Trophy className="size-6" />
            </span>
            <h2 className="tower-stage-title tower-stage-title--challenge">Challenges</h2>

            {workflowQuery.isLoading ? (
              <div className="mt-5">
                <TrialRoomSkeleton />
              </div>
            ) : null}
            {!workflowQuery.isLoading && workflowScenarios.length === 0 ? (
              <div className="mt-5">
                <EmptySection label="GIT Challenged" />
              </div>
            ) : null}

            <div className="challenge-room-stack">
              {workflowScenarios.map((scenario, index) => (
                <ChallengeTrial
                  index={index}
                  key={scenario.id}
                  locked={challengesLocked}
                  scenario={scenario}
                  storeyId={storey.id}
                />
              ))}
            </div>

            <div ref={workflowLoadRef} />
            {workflowQuery.isFetchingNextPage ? (
              <div className="mt-3">
                <TrialRoomSkeleton />
              </div>
            ) : null}
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

          {!isLast ? <TowerSectionSeparator afterChallenges continuation /> : <TowerSectionSeparator afterChallenges base />}
        </div>
      </div>
    </section>
  )
}
