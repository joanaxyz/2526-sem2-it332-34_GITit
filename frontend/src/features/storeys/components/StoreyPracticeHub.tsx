import { useEffect, useRef, useState } from 'react'
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
  difficultyLabel,
  nextReward,
  REWARD_MARKERS,
} from '@/features/storeys/challengeUi'
import { MonsterCrest, type MonsterVariant } from '@/features/storeys/components/MonsterCrest'
import { TowerArtifact } from '@/features/storeys/components/TowerArtifact'
import { TowerCrystal } from '@/features/storeys/components/TowerCrystal'
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

function monsterVariant(difficulty: string): MonsterVariant {
  if (difficulty === 'easy' || difficulty === 'medium' || difficulty === 'hard') return difficulty
  return 'hard'
}

// ── Command Adventure: a balcony gate with its own gabled roof + 3 dormer windows.
function AdventureBalcony({
  adventure,
  selected,
  onSelect,
}: {
  adventure: CommandAdventureSummary
  selected: boolean
  onSelect: () => void
}) {
  return (
    <button
      type="button"
      className="balcony"
      data-selected={selected ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select Command Adventure: ${adventure.title}`}
      onClick={onSelect}
    >
      <span className="balcony-roof" aria-hidden="true">
        <span className="balcony-roof-windows">
          <span className="balcony-roof-window" />
          <span className="balcony-roof-window" />
          <span className="balcony-roof-window" />
        </span>
      </span>
      <span className="balcony-door" aria-hidden="true">
        <span className="balcony-door-leaf" />
        <span className="balcony-door-glow" />
      </span>
      <span className="balcony-rail" aria-hidden="true">
        <span />
        <span />
        <span />
        <span />
        <span />
      </span>
      <span className="door-ring" aria-hidden="true" />
    </button>
  )
}

// ── A single GIT Challenged level door, crowned with a monster crest. ──
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

  return (
    <button
      type="button"
      className="trial-door"
      data-difficulty={difficulty}
      data-selected={selected ? 'true' : undefined}
      data-locked={locked || level.status === 'locked' ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select ${scenario.title}: ${difficultyLabel(level)}`}
      onClick={() => select({ kind: 'challenge', storeyId, scenarioIndex, scenario, level, locked })}
    >
      <MonsterCrest variant={monsterVariant(difficulty)} />
      <span className="trial-door-arch" aria-hidden="true">
        <span className="trial-door-leaf" />
        <span className="trial-door-glow" />
      </span>
      <span className="trial-door-label">{difficultyLabel(level)}</span>
      <span className="door-ring" aria-hidden="true" />
    </button>
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
    <motion.div
      className="trial-group"
      data-locked={locked ? 'true' : undefined}
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.44, delay: index * 0.04, ease: [0.16, 1, 0.3, 1] }}
    >
      <span className="trial-name">
        <span className="trial-name-index">Trial {index + 1}</span>
        {scenario.title}
      </span>
      <div className="trial-door-row">
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
      </div>
    </motion.div>
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

  const select = useTowerSelection((state) => state.select)
  const selectedAdventureId = useTowerSelection((state) =>
    state.selected?.kind === 'adventure' ? state.selected.adventure.id : null,
  )

  const challengesLocked = adventure !== null && adventure.status !== 'completed'
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
      <div
        className={cn('learning-tower', !isFirst && 'learning-tower-continuation', !isLast && 'learning-tower-continues')}
      >
        {isFirst ? <TowerArtifact /> : null}

        <motion.div
          className="tower-shell"
          initial={{ opacity: 0, y: 22, scale: 0.99 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ amount: 0.18, once: true, margin: '-6% 0px -6% 0px' }}
          transition={{ duration: 0.68, delay: motionDelay, ease: [0.16, 1, 0.3, 1] }}
        >
          <span className="tower-rim tower-rim--top" aria-hidden="true" />
          <span className="tower-facet tower-facet--left" aria-hidden="true" />
          <span className="tower-facet tower-facet--right" aria-hidden="true" />
          <span className="tower-rim tower-rim--bottom" aria-hidden="true" />

          <motion.section
            className="tower-floor adventure-floor"
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.42, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.03, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-wall-window tower-wall-window--l" aria-hidden="true" style={{ top: '6.2rem' }} />
            <span className="tower-wall-window tower-wall-window--r" aria-hidden="true" style={{ top: '6.2rem' }} />
            <span className="tower-floor-icon">
              <Swords className="size-7" />
            </span>
            <h2 className="tower-floor-title command-adventure-title">Command Adventure</h2>

            {adventureQuery.isLoading ? <LoadingRows compact /> : null}
            {!adventureQuery.isLoading && !adventure ? <EmptySection label="Command Adventures" /> : null}

            {adventure ? (
              <div className="tower-door-mount">
                <AdventureBalcony
                  adventure={adventure}
                  selected={adventureSelected}
                  onSelect={() => select({ kind: 'adventure', storeyId: storey.id, adventure })}
                />
              </div>
            ) : null}
          </motion.section>

          <motion.div
            className="tower-section-sep"
            aria-hidden="true"
            initial={{ opacity: 0, scaleX: 0.52 }}
            whileInView={{ opacity: 1, scaleX: 1 }}
            viewport={{ amount: 0.6, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.06, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="tower-section-sep-medallion" />
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

            {workflowQuery.isLoading ? <div className="mt-5"><LoadingRows /></div> : null}
            {!workflowQuery.isLoading && workflowScenarios.length === 0 ? (
              <div className="mt-5">
                <EmptySection label="GIT Challenged" />
              </div>
            ) : null}

            <div className="trial-stack">
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

        {isLast ? <TowerCrystal /> : <div className="tower-stack-connector" aria-hidden="true" />}
      </div>
    </section>
  )
}
