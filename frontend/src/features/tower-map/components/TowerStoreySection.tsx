import {
  memo,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type HTMLAttributes,
  type ReactNode,
} from 'react'
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
import { towerMapApi } from '@/features/tower-map/api/towerMapApi'
import { StoreyBookCard } from '@/features/tower-map/book/StoreyBookCard'
import type { LearningStorey } from '@/features/tower-map/types'
import { GitCoinIcon } from '@/features/wallet/components/GitCoinIcon'
import { HallArt } from '@/features/tower-map/components/art/HallArt'
import { PieceArt } from '@/features/tower-map/components/PieceArt'
import { TowerStoreySkeleton } from '@/features/tower-map/components/TowerStoreySkeleton'
import {
  pieceByType,
  pieceBySuffix,
  towerDescriptorFor,
  towerPieceAttrs,
} from '@/features/tower-map/components/towerPieceData'
import { assetsApi } from '@/shared/assets/assetsApi'
import type { TowerLayoutDescriptor, TowerLayoutPieceDescriptor, TowerPieceAssetDescriptor } from '@/shared/assets/types'
import {
  chestRewards,
  DIFFICULTY_ACCENT,
  difficultyLabel,
  nextReward,
} from '@/features/tower-map/challengeUi'
import { isSelected, useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'
import { ProgressBar } from '@/shared/components/ProgressBar'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

function EmptySection({ label }: { label: string }) {
  return <div className="tower-empty-state">No {label} published yet.</div>
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

const PIECE_EASE = [0.16, 1, 0.3, 1] as const
const EMPTY_TOMES: TomeSummary[] = []
const EMPTY_CHALLENGES: ChallengeSummary[] = []

// -- Roof crown: the one-off tower cap. The lit-window band is a separate
// backend piece so repeating storeys never repeat the roof. --
// `animate={false}` drops the scroll-entrance so the tower editor can reuse this
// exact markup as a static, selectable piece (extra props/children land on the
// root). The live tower passes neither, so its motion path is unchanged.
export function RoofSpire({
  piece,
  descriptor,
  animate = true,
  className,
  children,
  ...rest
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  animate?: boolean
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const variant = 'roof'
  const content = <PieceArt pieceType="spire" descriptor={descriptor} variant={variant} />

  if (!animate) {
    return (
      <div className={cn('tower-roof-stage', className)} {...towerPieceAttrs(piece, descriptor, { variant })} {...rest}>
        {content}
        {children}
      </div>
    )
  }

  return (
    <motion.div
      className="tower-roof-stage"
      {...towerPieceAttrs(piece, descriptor, { variant })}
      aria-hidden="true"
      initial={{ opacity: 0, y: -28, scale: 0.98 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.62, ease: PIECE_EASE }}
    >
      {content}
    </motion.div>
  )
}

// -- Windows storey: the lit-window band that tops every storey. --
export function WindowStorey({
  piece,
  descriptor,
  animate = true,
  className,
  children,
  ...rest
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  animate?: boolean
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const variant = 'regular'
  const content = <PieceArt pieceType="window_section" descriptor={descriptor} variant={variant} />

  if (!animate) {
    return (
      <div className={cn('tower-window-stage', className)} {...towerPieceAttrs(piece, descriptor, { variant })} {...rest}>
        {content}
        {children}
      </div>
    )
  }

  return (
    <motion.div
      className="tower-window-stage"
      {...towerPieceAttrs(piece, descriptor, { variant })}
      aria-hidden="true"
      initial={{ opacity: 0, y: -18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ amount: 0.3, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      {content}
    </motion.div>
  )
}

// Walkable landing between tower rooms. Challenge-after landings get physical
// crenels that keep their side outlines closed. The old separator class names
// remain as compatibility hooks for the current character controller.
export function TowerLanding({
  continuation = false,
  base = false,
  afterChallenges = false,
  piece,
  descriptor,
  animate = true,
  className,
  children,
  ...rest
}: {
  continuation?: boolean
  base?: boolean
  afterChallenges?: boolean
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  animate?: boolean
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const cls = cn(
    'tower-landing',
    'tower-section-separator',
    continuation && 'is-continuation',
    base && 'is-base',
    afterChallenges && 'is-after-challenges',
    className,
  )
  const variant = afterChallenges ? 'after-challenges' : 'regular'
  const content = <PieceArt pieceType="landing" descriptor={descriptor} variant={variant} />

  if (!animate) {
    return (
      <div className={cls} {...towerPieceAttrs(piece, descriptor, { variant })} {...rest}>
        {content}
        {children}
      </div>
    )
  }

  return (
    <motion.div
      className={cls}
      {...towerPieceAttrs(piece, descriptor, { variant })}
      aria-hidden="true"
      initial={{ opacity: 0, scaleX: 0.86 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      viewport={{ amount: 0.4, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      {content}
    </motion.div>
  )
}

// -- Command Adventure: a single arched neon gate, selectable. The gate
// materializes out of the wall when it scrolls into view. --
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
      <PieceArt pieceType="door" descriptor={descriptor} />
    </motion.button>
  )
}

// -- Tome: a singular lectern with an open book resting on it. Not a doorway -
// furniture you approach. Appears only on storeys where a tome is authored, so
// it never becomes a repeating pattern like the gate or the trial rooms. --
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
      <PieceArt pieceType="tome" descriptor={descriptor} />
      <span className="tome-lectern-label">{tome.title}</span>
    </motion.button>
  )
}

// The belt under the scriptorium carries a single carved keystone bearing the
// open-book sigil - quiet masonry, not decoration, and only tome storeys earn
// it. Drawn as SVG so the tapered keystone keeps its full neon outline.
export function TomeLanding({
  piece,
  descriptor,
  animate = true,
  className,
  children,
  ...rest
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  animate?: boolean
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const cls = cn('tower-landing', 'tower-tome-separator', className)
  const variant = 'tome'
  const content = <PieceArt pieceType="landing" descriptor={descriptor} variant={variant} />

  if (!animate) {
    return (
      <div className={cls} {...towerPieceAttrs(piece, descriptor, { variant })} {...rest}>
        {content}
        {children}
      </div>
    )
  }

  return (
    <motion.div
      className={cls}
      {...towerPieceAttrs(piece, descriptor, { variant })}
      aria-hidden="true"
      initial={{ opacity: 0, scaleX: 0.88 }}
      whileInView={{ opacity: 1, scaleX: 1 }}
      viewport={{ amount: 0.4, once: true }}
      transition={{ duration: 0.5, ease: PIECE_EASE }}
    >
      {content}
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
  const landingDescriptor = towerDescriptorFor(landingPiece, pieceDescriptors)
  return (
    <>
      <motion.section
        className="tower-tome-stage"
        initial={{ opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ amount: 0.42, once: true }}
        transition={{ duration: 0.5, ease: PIECE_EASE }}
      >
        <HallArt variant="tome" />
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

// -- A single Challenges level door - selectable, framed by difficulty color. --
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
      {/* Difficulty now reads from the gate art itself (distinct silhouette +
          engraved numeral + accent), so no text tag rides under the door. The
          aria-label still names it for assistive tech. */}
      <PieceArt pieceType="door" descriptor={descriptor} variant="portcullis" />
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
  gateDescriptor,
}: {
  challenge: ChallengeSummary
  index: number
  storeyId: number
  locked: boolean
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  /** The interactable gate asset for each level (the portcullis). */
  gateDescriptor?: TowerPieceAssetDescriptor | null
}) {
  return (
    <motion.article
      className="trial-room"
      {...towerPieceAttrs(piece, descriptor, { variant: 'challenge' })}
      initial={{ opacity: 0, y: 18, scale: 0.99 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ amount: 0.24, once: true }}
      transition={{ duration: 0.44, delay: index * 0.025, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* Title/summary stay out of the tower (terse by design); the "Trial N"
          kicker is gone too. Multiple trials are separated by the room's top
          hairline (`.trial-room::before`). */}
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
            descriptor={gateDescriptor}
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
          Storey overview for this Command Adventure and Challenge set.
        </p>
      </div>

      <section className="tower-side-panel storey-overview-card" aria-label={`${title} storey overview`}>
        <div className="grid gap-4">
          <OverviewStat icon={ListChecks} label="Command skills" value={storey.command_skill_count} />
          <OverviewStat icon={Swords} label="Challenges" value={storey.challenge_count} />
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

type TowerStoreySectionProps = {
  storey: LearningStorey
  displayTitle?: string
  isFirst?: boolean
  isLast?: boolean
  sequenceIndex?: number
}

function TowerStoreySectionInner({
  storey,
  displayTitle,
  isFirst = true,
  isLast = true,
  sequenceIndex = 0,
}: TowerStoreySectionProps) {
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
    queryFn: () => towerMapApi.getStoreyOverview(storey.id),
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
  // While the storey's content OR its piece art is still in flight, draw the
  // outline skeleton instead of the finished pieces. Gating the whole structure
  // (not just the doors) keeps loading from flashing the detailed fallback art —
  // and stops the crowned fallback from doubling the window band.
  const structureLoading = !shouldLoad || overviewQuery.isLoading || towerPiecesQuery.isLoading
  const towerPieceDescriptors = useMemo<Record<string, TowerPieceAssetDescriptor>>(() => {
    const descriptors: Record<string, TowerPieceAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(towerPiecesQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_piece') descriptors[slug] = descriptor
    }
    return descriptors
  }, [towerPiecesQuery.data])

  const layout = overview?.tower_layout ?? null
  const adventure: CommandAdventureSummary | null = overview?.command_adventure ?? null
  const rawTomes: TomeSummary[] = overview?.tomes ?? EMPTY_TOMES
  const rawChallenges: ChallengeSummary[] = overview?.challenges ?? EMPTY_CHALLENGES
  // Tomes render only where authored; each placement slot filters its own list,
  // so non-authored storeys keep the exact current layout.
  const tomesAboveAdventure = useMemo(
    () => orderedByLayout(rawTomes.filter((tome) => tome.placement === 'above_adventure'), layout, 'tome', 'tome'),
    [layout, rawTomes],
  )
  const challenges = useMemo(
    () => orderedByLayout(rawChallenges, layout, 'challenge', 'challenge_section'),
    [layout, rawChallenges],
  )
  const {
    tomePieceById,
    adventurePiece,
    tomeLandingPiece,
    adventureLandingPiece,
    challengePieceById,
    challengeStagePiece,
    challengeLandingPiece,
    spirePiece,
    windowPiece,
  } = useMemo(() => {
    const nextTomePieceById = contentPieceMap(layout, 'tome', 'tome')
    const adventurePieceById = contentPieceMap(layout, 'adventure', 'adventure_section')
    const nextChallengePieceById = contentPieceMap(layout, 'challenge', 'challenge_section')
    return {
      tomePieceById: nextTomePieceById,
      adventurePiece: adventure
        ? adventurePieceById.get(String(adventure.id))
        : pieceByType(layout, 'adventure_section'),
      tomeLandingPiece: pieceBySuffix(layout, 'landing-after-tomes'),
      adventureLandingPiece: pieceBySuffix(layout, 'landing-after-adventure'),
      challengePieceById: nextChallengePieceById,
      challengeStagePiece: challenges.length
        ? nextChallengePieceById.get(String(challenges[0].id))
        : pieceBySuffix(layout, 'challenges') ?? pieceByType(layout, 'challenge_section'),
      challengeLandingPiece: pieceBySuffix(layout, 'landing-after-challenges'),
      spirePiece: pieceByType(layout, 'spire'),
      windowPiece: pieceByType(layout, 'window_section'),
    }
  }, [adventure, challenges, layout])
  const spireDescriptor = towerDescriptorFor(spirePiece, towerPieceDescriptors)
  const windowDescriptor =
    towerDescriptorFor(windowPiece, towerPieceDescriptors) ?? towerPieceDescriptors['official-window-section'] ?? null
  const adventureDescriptor = towerDescriptorFor(adventurePiece, towerPieceDescriptors)
  const adventureLandingDescriptor = towerDescriptorFor(adventureLandingPiece, towerPieceDescriptors)
  const challengeStageDescriptor = towerDescriptorFor(challengeStagePiece, towerPieceDescriptors)
  const challengeLandingDescriptor = towerDescriptorFor(challengeLandingPiece, towerPieceDescriptors)
  const doorDescriptor = towerPieceDescriptors['official-door'] ?? null
  // The portcullis is its own asset (its own silhouette + slide-up animation).
  // Never fall back to the door art here: a door descriptor rendered with the
  // 'portcullis' variant would draw the swing-open gate, not a portcullis.
  const portcullisDescriptor = towerPieceDescriptors['official-portcullis'] ?? null

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
            entrance animation, so the storey assembles piece by piece — over the
            outline skeleton drawn while content + art load. */}
        <div className="tower-repeater">
          {structureLoading ? (
            <TowerStoreySkeleton isFirst={isFirst} />
          ) : (
            <>
              {isFirst ? <RoofSpire descriptor={spireDescriptor} piece={spirePiece} /> : null}
              <WindowStorey descriptor={windowDescriptor} piece={windowPiece} />

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
                {...towerPieceAttrs(adventurePiece, adventureDescriptor, { variant: 'adventure' })}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ amount: 0.42, once: true }}
                transition={{ duration: 0.5, delay: motionDelay + 0.03, ease: [0.16, 1, 0.3, 1] }}
              >
                <PieceArt pieceType="adventure_section" descriptor={adventureDescriptor} variant="adventure" />
                <span className="tower-stage-icon tower-stage-icon--cyan">
                  <Swords className="size-6" />
                </span>
                <h2 className="tower-stage-title tower-stage-title--adventure">Command Adventure</h2>

                {!adventure ? <EmptySection label="Command Adventures" /> : null}

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
                {...towerPieceAttrs(challengeStagePiece, challengeStageDescriptor, { variant: 'challenge' })}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ amount: 0.16, once: true, margin: '-6% 0px -6% 0px' }}
                transition={{ duration: 0.58, delay: motionDelay + 0.08, ease: [0.16, 1, 0.3, 1] }}
              >
                <PieceArt pieceType="challenge_section" descriptor={challengeStageDescriptor} variant="challenge" />
                <span className="tower-stage-icon tower-stage-icon--purple">
                  <Trophy className="size-6" />
                </span>
                <h2 className="tower-stage-title tower-stage-title--challenge">Challenges</h2>

                {challenges.length === 0 ? (
                  <div className="mt-5">
                    <EmptySection label="Challenges" />
                  </div>
                ) : null}

                <div className="challenge-room-stack">
                  {challenges.map((challenge, index) => (
                    <ChallengeTrial
                      index={index}
                      key={challenge.id}
                      locked={challengesLocked}
                      descriptor={towerDescriptorFor(challengePieceById.get(String(challenge.id)), towerPieceDescriptors)}
                      gateDescriptor={portcullisDescriptor}
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
            </>
          )}
        </div>
      </div>
    </section>
  )
}

export const TowerStoreySection = memo(TowerStoreySectionInner)
TowerStoreySection.displayName = 'TowerStoreySection'
