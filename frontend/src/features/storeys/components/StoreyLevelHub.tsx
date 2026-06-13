import { useEffect, useRef, useState, type CSSProperties } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BookOpen,
  Layers3,
  ListChecks,
  Swords,
  Trophy,
  type LucideIcon,
} from 'lucide-react'
import { motion, useInView } from 'motion/react'

import rewardChest from '@/assets/images/reward-chest-neon.png'
import type {
  ChallengeLevelAccess,
  ChallengeSummary,
  CommandAdventureSummary,
  TomeSummary,
} from '@/features/challenges/types'
import { storeysApi } from '@/features/storeys/api/storeysApi'
import { StoreyBookCard } from '@/features/storeys/book/StoreyBookCard'
import type { LearningStorey } from '@/features/storeys/types'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import {
  AdventureSectionPiece,
  ChallengeSectionPiece,
  DoorPiece,
  LandingPiece,
  SpirePiece,
  TomePiece,
  towerDescriptorFor,
  towerPieceAttrs,
} from '@/features/storeys/components/TowerPieces'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { TowerLayoutDescriptor, TowerLayoutPieceDescriptor, TowerPieceAssetDescriptor } from '@/shared/assets/types'
import {
  actionForChallengeLevel,
  actionLabel,
  chestRewards,
  DIFFICULTY_ACCENT,
  difficultyLabel,
  nextReward,
} from '@/features/storeys/challengeUi'
import { TomeLecternArt } from '@/features/storeys/components/TomeLecternArt'
import { isSelected, useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

function EmptySection({ label }: { label: string }) {
  return <div className="tower-empty-state">No {label} published yet.</div>
}

function pieceByType(layout: TowerLayoutDescriptor | null, pieceType: TowerLayoutPieceDescriptor['pieceType']) {
  return layout?.pieces.find((piece) => piece.pieceType === pieceType) ?? null
}

function pieceBySuffix(layout: TowerLayoutDescriptor | null, suffix: string) {
  return layout?.pieces.find((piece) => piece.instanceId.endsWith(suffix)) ?? null
}

function contentPieceMap(
  layout: TowerLayoutDescriptor | null,
  kind: NonNullable<TowerLayoutPieceDescriptor['contentBinding']>['kind'],
  pieceType: TowerLayoutPieceDescriptor['pieceType'],
) {
  const entries = (layout?.pieces ?? []).flatMap((piece) => {
    const binding = piece.contentBinding
    return binding?.kind === kind && piece.pieceType === pieceType ? [[String(binding.id), piece] as const] : []
  })
  return new Map(entries)
}

function orderedByLayout<T extends { id: number | string }>(
  items: T[],
  layout: TowerLayoutDescriptor | null,
  kind: NonNullable<TowerLayoutPieceDescriptor['contentBinding']>['kind'],
  pieceType: TowerLayoutPieceDescriptor['pieceType'],
) {
  if (!layout) return items
  const byId = new Map(items.map((item) => [String(item.id), item]))
  const ordered = layout.pieces.flatMap((piece) => {
    const binding = piece.contentBinding
    const item = binding?.kind === kind && piece.pieceType === pieceType ? byId.get(String(binding.id)) : null
    return item ? [item] : []
  })
  if (ordered.length !== items.length) return items
  return ordered
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

const PIECE_EASE = [0.16, 1, 0.3, 1] as const

// ── Windows storey: the lit-window band that tops every storey; the conical roof
// only crowns the very first storey (the top of the whole tower). ──
function WindowStorey({
  crowned,
  piece,
  descriptor,
}: {
  crowned: boolean
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.div
      className="tower-window-stage"
      {...towerPieceAttrs(piece, descriptor)}
      aria-hidden="true"
      initial={{ opacity: 0, y: -22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.55, ease: PIECE_EASE }}
    >
      <SpirePiece descriptor={descriptor} />
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

// Walkable landing between tower rooms. Challenge-after landings get physical
// crenels that keep their side outlines closed. The old separator class names
// remain as compatibility hooks for the current character controller.
function TowerLanding({
  continuation = false,
  base = false,
  afterChallenges = false,
  piece,
  descriptor,
}: {
  continuation?: boolean
  base?: boolean
  afterChallenges?: boolean
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.div
      className={cn(
        'tower-landing',
        'tower-section-separator',
        continuation && 'is-continuation',
        base && 'is-base',
        afterChallenges && 'is-after-challenges',
      )}
      {...towerPieceAttrs(piece, descriptor)}
      aria-hidden="true"
      initial={{ opacity: 0, scaleX: 0.86 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      viewport={{ amount: 0.4, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      <LandingPiece descriptor={descriptor} />
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
  piece,
  descriptor,
}: {
  adventure: CommandAdventureSummary
  selected: boolean
  onSelect: () => void
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.button
      type="button"
      className="adventure-door"
      {...towerPieceAttrs(piece, descriptor)}
      data-selected={selected ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select Command Adventure: ${adventure.title}`}
      onClick={onSelect}
      initial={{ opacity: 0, y: 26, scale: 0.9, rotateX: -18, transformPerspective: 760 }}
      whileInView={{ opacity: 1, y: 0, scale: 1, rotateX: 0, transformPerspective: 760 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.62, ease: PIECE_EASE }}
    >
      <DoorPiece descriptor={descriptor} />
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

// ── Tome: a singular lectern with an open book resting on it. Not a doorway —
// furniture you approach. Appears only on storeys where a tome is authored, so
// it never becomes a repeating pattern like the gate or the trial rooms. ──
function TomeArtifact({
  tome,
  storeyId,
  piece,
  descriptor,
}: {
  tome: TomeSummary
  storeyId: number
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  const select = useTowerSelection((state) => state.select)
  const selected = useTowerSelection((state) =>
    isSelected(state.selected, { kind: 'tome', storeyId, tome }),
  )
  return (
    <motion.button
      type="button"
      className="tome-lectern"
      {...towerPieceAttrs(piece, descriptor)}
      data-selected={selected ? 'true' : undefined}
      aria-pressed={selected}
      aria-label={`Select Tome: ${tome.title}`}
      onClick={() => select({ kind: 'tome', storeyId, tome })}
      initial={{ opacity: 0, y: 24, scale: 0.92, rotateX: -14, transformPerspective: 720 }}
      whileInView={{ opacity: 1, y: 0, scale: 1, rotateX: 0, transformPerspective: 720 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.58, ease: PIECE_EASE }}
    >
      <TomePiece descriptor={descriptor} />
      <TomeLecternArt />
      <span className="tome-lectern-label">{tome.title}</span>
    </motion.button>
  )
}

// The belt under the scriptorium carries a single carved keystone bearing the
// open-book sigil — quiet masonry, not decoration, and only tome storeys earn
// it. Drawn as SVG so the tapered keystone keeps its full neon outline.
function TomeLanding({
  piece,
  descriptor,
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.div
      className="tower-landing tower-tome-separator"
      {...towerPieceAttrs(piece, descriptor)}
      aria-hidden="true"
      initial={{ opacity: 0, scaleX: 0.88 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      viewport={{ amount: 0.4, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      <LandingPiece descriptor={descriptor} />
      <span className="tower-tome-separator-beam" />
      <span className="tower-tome-separator-keystone">
        <svg viewBox="0 0 56 46" aria-hidden="true" focusable="false">
          <path
            d="M4 1 H52 L45 45 H11 Z"
            fill="#0a2238"
            stroke="rgba(45, 245, 255, 0.94)"
            strokeWidth="2"
            strokeLinejoin="round"
          />
          <path
            d="M28 14 C25 11.6 20.4 11.1 16.6 12.4 L16.6 27 C20.4 25.7 25 26.2 28 28.6 C31 26.2 35.6 25.7 39.4 27 L39.4 12.4 C35.6 11.1 31 11.6 28 14 Z"
            fill="rgba(2, 12, 22, 0.6)"
            stroke="rgba(45, 245, 255, 0.62)"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
          <path d="M28 14 V28.6" stroke="rgba(45, 245, 255, 0.45)" strokeWidth="1.3" />
        </svg>
      </span>
      <span className="tower-tome-separator-ledge" />
    </motion.div>
  )
}

function TomeSection({
  tomes,
  storeyId,
  pieceByTomeId,
  landingPiece,
  pieceDescriptors,
}: {
  tomes: TomeSummary[]
  storeyId: number
  pieceByTomeId: Map<string, TowerLayoutPieceDescriptor>
  landingPiece?: TowerLayoutPieceDescriptor | null
  pieceDescriptors: Record<string, TowerPieceAssetDescriptor>
}) {
  const sectionPiece = tomes.length ? pieceByTomeId.get(String(tomes[0].id)) : null
  const sectionDescriptor = towerDescriptorFor(sectionPiece, pieceDescriptors)
  const landingDescriptor = towerDescriptorFor(landingPiece, pieceDescriptors)
  return (
    <>
      <motion.section
        className="tower-tome-stage"
        {...towerPieceAttrs(sectionPiece, sectionDescriptor)}
        initial={{ opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ amount: 0.42, once: true }}
        transition={{ duration: 0.5, ease: PIECE_EASE }}
      >
        <TomePiece descriptor={sectionDescriptor} />
        <span className="tower-stage-icon tower-stage-icon--cyan">
          <BookOpen className="size-6" />
        </span>
        <h2 className="tower-stage-title tower-stage-title--tome">Tome</h2>
        <div className="tower-tome-row">
          {tomes.map((tome) => (
            <TomeArtifact
              key={tome.id}
              descriptor={towerDescriptorFor(pieceByTomeId.get(String(tome.id)), pieceDescriptors)}
              piece={pieceByTomeId.get(String(tome.id))}
              tome={tome}
              storeyId={storeyId}
            />
          ))}
        </div>
      </motion.section>
      <TomeLanding descriptor={landingDescriptor} piece={landingPiece} />
    </>
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
  challenge,
  challengeIndex,
  level,
  storeyId,
  locked,
  descriptor,
}: {
  challenge: ChallengeSummary
  challengeIndex: number
  level: ChallengeLevelAccess
  storeyId: number
  locked: boolean
  descriptor?: TowerPieceAssetDescriptor | null
}) {
  const select = useTowerSelection((state) => state.select)
  const selected = useTowerSelection((state) =>
    isSelected(state.selected, { kind: 'challenge', storeyId, challengeIndex, challenge, level, locked }),
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
      aria-label={`Select ${challenge.title}: ${difficultyLabel(level)}`}
      onClick={() => select({ kind: 'challenge', storeyId, challengeIndex, challenge, level, locked })}
      variants={trialDoorVariants}
    >
      <DoorPiece descriptor={descriptor} />
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
  challenge,
  index,
  storeyId,
  locked,
  piece,
  descriptor,
  doorDescriptor,
}: {
  challenge: ChallengeSummary
  index: number
  storeyId: number
  locked: boolean
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  doorDescriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.article
      className="trial-room"
      {...towerPieceAttrs(piece, descriptor)}
      initial={{ opacity: 0, y: 18, scale: 0.99 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.24, once: true }}
      transition={{ duration: 0.44, delay: index * 0.025, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="trial-room-header">
        <span className="trial-room-kicker">Trial {index + 1}</span>
        <h3 className="trial-room-title">{challenge.title}</h3>
      </div>
      {challenge.summary?.trim() ? <p className="trial-room-summary">{challenge.summary}</p> : null}
      <motion.div
        className="trial-door-row"
        initial="hidden"
        whileInView="shown"
        viewport={{ amount: 0.3, once: true }}
        variants={trialDoorRowVariants}
      >
        {challenge.levels.map((level) => (
          <TrialDoor
            key={level.id}
            challenge={challenge}
            challengeIndex={index}
            level={level}
            storeyId={storeyId}
            locked={locked}
            descriptor={doorDescriptor}
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
  const rewards = chestRewards(storey)
  const reward = nextReward(rewards, progress)
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
              {rewards.map((chest) => (
                <span
                  className={chest.threshold <= progress ? 'is-earned' : undefined}
                  key={chest.threshold}
                  style={{ left: `${chest.threshold}%` }}
                >
                  <img src={rewardChest} alt="" />
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="stage-reward-panel" aria-label={`${title} progress reward`}>
        <div>
          <p className="text-sm text-muted-foreground">Progress Reward</p>
          <p className="mt-2 text-sm font-semibold text-foreground">Next chest at {reward.threshold}% storey progress</p>
          <p
            className="mt-3 inline-flex items-center gap-2 text-2xl font-black"
            style={{
              color: '#00F5D4',
              textShadow: '0 0 16px rgba(0, 245, 212, 0.45)',
            }}
          >
            +{reward.coins} coins
            <GitCoinIcon className="size-6 drop-shadow-[0_0_6px_rgba(0,245,212,0.4)]" />
          </p>
        </div>
        <span className="stage-reward-icon">
          <img className="stage-reward-chest" src={rewardChest} alt="" aria-hidden="true" />
        </span>
      </section>

      <StoreyBookCard storeyId={storey.id} storeyTitle={title} commandCount={storey.command_skill_count} />
    </motion.aside>
  )
}

type StoreyLevelHubProps = {
  storey: LearningStorey
  displayTitle?: string
  isFirst?: boolean
  isLast?: boolean
  sequenceIndex?: number
}

export function StoreyLevelHub({
  storey,
  displayTitle,
  isFirst = true,
  isLast = true,
  sequenceIndex = 0,
}: StoreyLevelHubProps) {
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

  // One request per storey: the Command Adventure, tomes, and challenges arrive
  // together instead of as 2-3 separate round trips.
  const overviewQuery = useQuery({
    queryKey: queryKeys.storeyOverview(storey.id),
    queryFn: () => storeysApi.getStoreyOverview(storey.id),
    enabled: shouldLoad,
    staleTime: 2 * 60 * 1000,
  })
  const towerPiecesQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('tower_piece'),
    queryFn: () => assetsApi.getDescriptors('tower_piece'),
    enabled: shouldLoad,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })
  const overview = overviewQuery.data ?? null
  const contentLoading = !shouldLoad || overviewQuery.isLoading
  const towerPieceDescriptors: Record<string, TowerPieceAssetDescriptor> = {}
  for (const [slug, descriptor] of Object.entries(towerPiecesQuery.data?.results ?? {})) {
    if (descriptor.kind === 'tower_piece') towerPieceDescriptors[slug] = descriptor
  }

  const layout = overview?.tower_layout ?? null
  const adventure: CommandAdventureSummary | null = overview?.command_adventure ?? null
  const rawChallenges: ChallengeSummary[] = overview?.challenges ?? []
  // Tomes render only where authored; each placement slot filters its own list,
  // so non-authored storeys keep the exact current layout.
  const tomesAboveAdventure: TomeSummary[] = orderedByLayout(
    (overview?.tomes ?? []).filter((tome) => tome.placement === 'above_adventure'),
    layout,
    'tome',
    'tome',
  )
  const challenges: ChallengeSummary[] = orderedByLayout(
    rawChallenges,
    layout,
    'challenge',
    'challenge_section',
  )
  const tomePieceById = contentPieceMap(layout, 'tome', 'tome')
  const adventurePieceById = contentPieceMap(layout, 'adventure', 'adventure_section')
  const challengePieceById = contentPieceMap(layout, 'challenge', 'challenge_section')
  const spirePiece = pieceByType(layout, 'spire')
  const adventurePiece = adventure
    ? adventurePieceById.get(String(adventure.id))
    : pieceByType(layout, 'adventure_section')
  const tomeLandingPiece = pieceBySuffix(layout, 'landing-after-tomes')
  const adventureLandingPiece = pieceBySuffix(layout, 'landing-after-adventure')
  const challengeStagePiece = challenges.length
    ? challengePieceById.get(String(challenges[0].id))
    : pieceBySuffix(layout, 'challenges') ?? pieceByType(layout, 'challenge_section')
  const challengeLandingPiece = pieceBySuffix(layout, 'landing-after-challenges')
  const spireDescriptor = towerDescriptorFor(spirePiece, towerPieceDescriptors)
  const adventureDescriptor = towerDescriptorFor(adventurePiece, towerPieceDescriptors)
  const adventureLandingDescriptor = towerDescriptorFor(adventureLandingPiece, towerPieceDescriptors)
  const challengeStageDescriptor = towerDescriptorFor(challengeStagePiece, towerPieceDescriptors)
  const challengeLandingDescriptor = towerDescriptorFor(challengeLandingPiece, towerPieceDescriptors)
  const doorDescriptor = towerPieceDescriptors['official-door'] ?? null

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
        {/* Each tower piece (window band, stages, landings, doors) owns its
            entrance animation, so the storey assembles piece by piece. */}
        <div className="tower-repeater">
          <WindowStorey crowned={isFirst} descriptor={spireDescriptor} piece={spirePiece} />

          {tomesAboveAdventure.length > 0 ? (
            <TomeSection
              landingPiece={tomeLandingPiece}
              pieceByTomeId={tomePieceById}
              pieceDescriptors={towerPieceDescriptors}
              tomes={tomesAboveAdventure}
              storeyId={storey.id}
            />
          ) : null}

          <motion.section
            className="tower-adventure-stage"
            {...towerPieceAttrs(adventurePiece, adventureDescriptor)}
            initial={{ opacity: 0, y: 14 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.42, once: true }}
            transition={{ duration: 0.5, delay: motionDelay + 0.03, ease: [0.16, 1, 0.3, 1] }}
          >
            <AdventureSectionPiece descriptor={adventureDescriptor} />
            <span className="tower-stage-icon tower-stage-icon--cyan">
              <Swords className="size-6" />
            </span>
            <h2 className="tower-stage-title tower-stage-title--adventure">Command Adventure</h2>

            {contentLoading ? <AdventureDoorSkeleton /> : null}
            {!contentLoading && !adventure ? <EmptySection label="Command Adventures" /> : null}

            {adventure ? (
              <div className="tower-adventure-door-wrap">
                <AdventureDoor
                  adventure={adventure}
                  descriptor={doorDescriptor}
                  piece={adventurePiece}
                  selected={adventureSelected}
                  onSelect={() => select({ kind: 'adventure', storeyId: storey.id, adventure })}
                />
              </div>
            ) : null}
          </motion.section>

          <TowerLanding descriptor={adventureLandingDescriptor} piece={adventureLandingPiece} />

          <motion.section
            className={cn('tower-challenges-stage', challengesLocked && 'is-locked')}
            {...towerPieceAttrs(challengeStagePiece, challengeStageDescriptor)}
            initial={{ opacity: 0, y: 18 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ amount: 0.16, once: true, margin: '-6% 0px -6% 0px' }}
            transition={{ duration: 0.58, delay: motionDelay + 0.08, ease: [0.16, 1, 0.3, 1] }}
          >
            <ChallengeSectionPiece descriptor={challengeStageDescriptor} />
            <span className="tower-stage-icon tower-stage-icon--purple">
              <Trophy className="size-6" />
            </span>
            <h2 className="tower-stage-title tower-stage-title--challenge">Challenges</h2>

            {contentLoading ? (
              <div className="mt-5">
                <TrialRoomSkeleton />
              </div>
            ) : null}
            {!contentLoading && challenges.length === 0 ? (
              <div className="mt-5">
                <EmptySection label="GIT Challenged" />
              </div>
            ) : null}

            <div className="challenge-room-stack">
              {challenges.map((challenge, index) => (
                <ChallengeTrial
                  index={index}
                  key={challenge.id}
                  locked={challengesLocked}
                  descriptor={towerDescriptorFor(challengePieceById.get(String(challenge.id)), towerPieceDescriptors)}
                  doorDescriptor={doorDescriptor}
                  piece={challengePieceById.get(String(challenge.id))}
                  challenge={challenge}
                  storeyId={storey.id}
                />
              ))}
            </div>
          </motion.section>

          {!isLast ? (
            <TowerLanding
              afterChallenges
              continuation
              descriptor={challengeLandingDescriptor}
              piece={challengeLandingPiece}
            />
          ) : (
            <TowerLanding afterChallenges base descriptor={challengeLandingDescriptor} piece={challengeLandingPiece} />
          )}
        </div>
      </div>
    </section>
  )
}
