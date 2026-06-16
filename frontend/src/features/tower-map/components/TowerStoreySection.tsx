import { memo, useEffect, useMemo, useRef, useState, type CSSProperties, type HTMLAttributes, type ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, Swords, Trophy } from 'lucide-react'

import type {
  ChallengeLevelAccess,
  ChallengeSummary,
  CommandAdventureSummary,
  TomeSummary,
} from '@/features/challenges/types'
import type { ArtifactPlacementDescriptor } from '@/features/tower-designs/types'
import { towerMapApi } from '@/features/tower-map/api/towerMapApi'
import type { LearningStorey } from '@/features/tower-map/types'
import { PieceArt } from '@/features/tower-map/components/PieceArt'
import { TowerArtifact } from '@/features/tower-map/components/TowerArtifact'
import { TowerStoreySkeleton } from '@/features/tower-map/components/TowerStoreySkeleton'
import {
  challengeLevelAccent,
  difficultyLabel,
} from '@/features/tower-map/challengeUi'
import { isSelected, useTowerSelection } from '@/features/tower-map/hooks/useTowerSelection'
import {
  pieceAspectRatio,
  pieceVariant,
  pieceTransformStyle,
  pieceViewBox,
  towerDescriptorFor,
  towerPieceAttrs,
} from '@/features/tower-map/components/towerPieceData'
import { assetsApi } from '@/shared/assets/assetsApi'
import type {
  TowerArtifactAssetDescriptor,
  TowerArtifactRole,
  TowerLayoutDescriptor,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { cn } from '@/shared/utils/cn'

const EMPTY_TOMES: TomeSummary[] = []
const EMPTY_CHALLENGES: ChallengeSummary[] = []

export function RoofSpire({
  piece,
  descriptor,
  className,
  children,
  style,
  ...rest
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const variant = 'roof'
  return (
    <div
      className={cn('tower-roof-stage', className)}
      style={{ ...(style ?? {}), ...(pieceTransformStyle(piece) ?? {}) }}
      {...towerPieceAttrs(piece, descriptor, { variant })}
      {...rest}
    >
      <PieceArt pieceType="crown" descriptor={descriptor} variant={variant} />
      {children}
      <PieceForeground piece={piece} descriptor={descriptor} variant={variant} />
    </div>
  )
}

export function TowerLanding({
  continuation = false,
  base = false,
  variant,
  piece,
  descriptor,
  className,
  children,
  style,
  ...rest
}: {
  continuation?: boolean
  base?: boolean
  variant?: string
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const renderVariant = variant ?? (piece ? pieceVariant(null, piece) : 'regular')
  return (
    <div
      className={cn(
        'tower-landing',
        'tower-section-separator',
        continuation && 'is-continuation',
        base && 'is-base',
        className,
      )}
      style={{ ...(style ?? {}), ...(pieceTransformStyle(piece) ?? {}) }}
      {...towerPieceAttrs(piece, descriptor, { variant: renderVariant })}
      {...rest}
    >
      <PieceArt pieceType="landing" descriptor={descriptor} variant={renderVariant} />
      {children}
      <PieceForeground piece={piece} descriptor={descriptor} variant={renderVariant} />
    </div>
  )
}

export function TowerBase({
  piece,
  descriptor,
  className,
  children,
  style,
  ...rest
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  children?: ReactNode
} & HTMLAttributes<HTMLDivElement>) {
  const variant = piece ? pieceVariant(null, piece) : 'base'
  return (
    <div
      className={cn('tower-base-stage', 'tower-section-separator', 'is-base', className)}
      style={{ ...(style ?? {}), ...(pieceTransformStyle(piece) ?? {}) }}
      {...towerPieceAttrs(piece, descriptor, { variant })}
      {...rest}
    >
      <PieceArt pieceType="base" descriptor={descriptor} variant={variant} />
      {children}
      <PieceForeground piece={piece} descriptor={descriptor} variant={variant} />
    </div>
  )
}

type BlueOccluderRegion = {
  id?: string
  x?: number
  y?: number
  width?: number
  height?: number
}

function PieceForeground({
  piece,
  descriptor,
  variant,
}: {
  piece?: TowerLayoutPieceDescriptor | null
  descriptor?: TowerPieceAssetDescriptor | null
  variant?: string
}) {
  const regions = blueOccluders(piece)
  if (!regions.length) return null
  return (
    <>
      {regions.map((region, index) => (
        <span
          className="tower-piece-foreground"
          key={region.id ?? index}
          style={occluderClipStyle(region, descriptor, variant)}
          aria-hidden="true"
        >
          <PieceArt pieceType={piece?.pieceType ?? 'section'} descriptor={descriptor} variant={variant} />
        </span>
      ))}
    </>
  )
}

function blueOccluders(piece?: TowerLayoutPieceDescriptor | null): BlueOccluderRegion[] {
  const value = piece?.config?.blue_occluders
  if (!Array.isArray(value)) return []
  return value.filter((item): item is BlueOccluderRegion => {
    if (typeof item !== 'object' || item === null) return false
    const region = item as BlueOccluderRegion
    return positive(region.width) !== null && positive(region.height) !== null
  })
}

function occluderClipStyle(
  region: BlueOccluderRegion,
  descriptor?: TowerPieceAssetDescriptor | null,
  variant?: string,
): CSSProperties {
  const box = pieceViewBox(descriptor, variant)
  const x = finite(region.x) ?? box.x
  const y = finite(region.y) ?? box.y
  const width = positive(region.width) ?? box.width
  const height = positive(region.height) ?? box.height
  const left = ((x - box.x) / Math.max(box.width, 1)) * 100
  const top = ((y - box.y) / Math.max(box.height, 1)) * 100
  const right = 100 - ((x + width - box.x) / Math.max(box.width, 1)) * 100
  const bottom = 100 - ((y + height - box.y) / Math.max(box.height, 1)) * 100
  return {
    clipPath: `inset(${top}% ${right}% ${bottom}% ${left}%)`,
  }
}

function finite(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function positive(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

export function TowerSectionShell({
  piece,
  descriptor,
  artifactRole = 'normal',
  className,
  children,
  style,
  ...rest
}: {
  piece: TowerLayoutPieceDescriptor
  descriptor?: TowerPieceAssetDescriptor | null
  artifactRole?: TowerArtifactRole
  children?: ReactNode
} & HTMLAttributes<HTMLElement>) {
  const roleClass =
    artifactRole === 'challenge' ? 'tower-challenges-stage' : artifactRole === 'tome' ? 'tower-tome-stage' : 'tower-adventure-stage'
  const title =
    artifactRole === 'challenge' ? 'Challenges' : artifactRole === 'tome' ? 'Tome' : artifactRole === 'adventure' ? 'Command Adventure' : ''
  const Icon = artifactRole === 'challenge' ? Trophy : artifactRole === 'tome' ? BookOpen : Swords
  const variant = artifactRole === 'normal' ? pieceVariant(null, piece) : artifactRole
  const frameStyle = {
    ...(style ?? {}),
    '--tower-piece-aspect': pieceAspectRatio(descriptor, variant),
    ...(pieceTransformStyle(piece) ?? {}),
  } as CSSProperties
  return (
    <section
      className={cn(roleClass, artifactRole === 'normal' && 'tower-generic-stage', className)}
      style={frameStyle}
      {...towerPieceAttrs(piece, descriptor, { variant })}
      {...rest}
    >
      <PieceArt pieceType="section" descriptor={descriptor} variant={variant} />
      {artifactRole !== 'normal' ? (
        <>
          <span className={cn('tower-stage-icon', artifactRole === 'challenge' ? 'tower-stage-icon--purple' : 'tower-stage-icon--cyan')}>
            <Icon className="size-6" />
          </span>
          <h2 className={cn('tower-stage-title', `tower-stage-title--${artifactRole}`)}>{title}</h2>
        </>
      ) : null}
      {children}
      <PieceForeground piece={piece} descriptor={descriptor} variant={variant} />
    </section>
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
}: TowerStoreySectionProps) {
  const hubRef = useRef<HTMLElement | null>(null)
  const [shouldLoad, setShouldLoad] = useState(false)

  useEffect(() => {
    const el = hubRef.current
    if (!el) return
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) setShouldLoad(true)
      },
      { rootMargin: '600px 0px 600px 0px' },
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

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
  const towerArtifactsQuery = useQuery({
    queryKey: queryKeys.assetDescriptors('tower_artifact'),
    queryFn: () => assetsApi.getDescriptors('tower_artifact'),
    enabled: shouldLoad,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })

  const overview = overviewQuery.data ?? null
  const structureLoading = !shouldLoad || overviewQuery.isLoading || towerPiecesQuery.isLoading
  const pieceDescriptors = useMemo<Record<string, TowerPieceAssetDescriptor>>(() => {
    const descriptors: Record<string, TowerPieceAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(towerPiecesQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_piece') descriptors[slug] = descriptor
    }
    return descriptors
  }, [towerPiecesQuery.data])
  const artifactDescriptors = useMemo<Record<string, TowerArtifactAssetDescriptor>>(() => {
    const descriptors: Record<string, TowerArtifactAssetDescriptor> = {}
    for (const [slug, descriptor] of Object.entries(towerArtifactsQuery.data?.results ?? {})) {
      if (descriptor.kind === 'tower_artifact') descriptors[slug] = descriptor
    }
    return descriptors
  }, [towerArtifactsQuery.data])

  const layout = overview?.tower_layout ?? null
  const artifactsByTarget = useMemo(() => groupArtifacts(overview?.artifacts ?? []), [overview?.artifacts])
  const adventures: CommandAdventureSummary[] = overview?.command_adventures ?? (
    overview?.command_adventure ? [overview.command_adventure] : []
  )
  const tomes: TomeSummary[] = overview?.tomes ?? EMPTY_TOMES
  const challenges: ChallengeSummary[] = overview?.challenges ?? EMPTY_CHALLENGES
  const challengesLocked = adventures.length > 0 && adventures.some((adventure) => !adventure.is_passed)
  const title = displayTitle ?? storey.title

  return (
    <section ref={hubRef} className="storey-section" aria-label={`${title} storey`} data-storey-id={storey.id}>
      <div className={cn('learning-tower', !isFirst && 'learning-tower-continuation')}>
        <div className="tower-repeater">
          {structureLoading || !layout ? (
            <TowerStoreySkeleton isFirst={isFirst} />
          ) : (
            <RenderedPieces
              artifactsByTarget={artifactsByTarget}
              artifactDescriptors={artifactDescriptors}
              challenges={challenges}
              challengesLocked={challengesLocked}
              isFirst={isFirst}
              isLast={isLast}
              layout={layout}
              pieceDescriptors={pieceDescriptors}
              storeyId={storey.id}
              adventures={adventures}
              tomes={tomes}
            />
          )}
        </div>
      </div>
    </section>
  )
}

function RenderedPieces({
  layout,
  pieceDescriptors,
  artifactDescriptors,
  artifactsByTarget,
  storeyId,
  adventures,
  tomes,
  challenges,
  challengesLocked,
  isFirst,
  isLast,
}: {
  layout: TowerLayoutDescriptor
  pieceDescriptors: Record<string, TowerPieceAssetDescriptor>
  artifactDescriptors: Record<string, TowerArtifactAssetDescriptor>
  artifactsByTarget: Map<string, ArtifactPlacementDescriptor[]>
  storeyId: number
  adventures: CommandAdventureSummary[]
  tomes: TomeSummary[]
  challenges: ChallengeSummary[]
  challengesLocked: boolean
  isFirst: boolean
  isLast: boolean
}) {
  const hasBasePiece = layout.pieces.some((piece) => piece.pieceType === 'base')
  return (
    <>
      {layout.pieces.map((piece) => {
        const descriptor = towerDescriptorFor(piece, pieceDescriptors)
        const artifacts = artifactsByTarget.get(piece.instanceId) ?? []
        const sectionRole = firstInteractableRole(artifacts)
        const children = artifacts.map((artifact) => (
          <PlayableArtifact
            key={artifact.id}
            artifact={artifact}
            descriptor={artifactDescriptors[artifact.assetSlug] ?? null}
            piece={piece}
            pieceDescriptor={descriptor}
            role={artifact.role}
            storeyId={storeyId}
            adventures={adventures}
            tomes={tomes}
            challenges={challenges}
            challengesLocked={challengesLocked}
          />
        ))
        if (piece.pieceType === 'crown') {
          return isFirst ? (
            <RoofSpire key={piece.instanceId} descriptor={descriptor} piece={piece}>
              {children}
            </RoofSpire>
          ) : null
        }
        if (piece.pieceType === 'base') {
          return isLast ? (
            <TowerBase key={piece.instanceId} descriptor={descriptor} piece={piece}>
              {children}
            </TowerBase>
          ) : null
        }
        if (piece.pieceType === 'landing') {
          const landing = (
            <TowerLanding
              key={piece.instanceId}
              variant={pieceVariant(layout, piece)}
              continuation={!isLast}
              base={isLast && !hasBasePiece}
              descriptor={descriptor}
              piece={piece}
            >
              {children}
            </TowerLanding>
          )
          return landing
        }
        return (
          <TowerSectionShell key={piece.instanceId} artifactRole={sectionRole} descriptor={descriptor} piece={piece}>
            {children}
            {sectionRole !== 'normal' && artifacts.length === 0 ? <div className="tower-empty-state">No content yet.</div> : null}
          </TowerSectionShell>
        )
      })}
    </>
  )
}

function PlayableArtifact({
  artifact,
  descriptor,
  piece,
  pieceDescriptor,
  role,
  storeyId,
  adventures,
  tomes,
  challenges,
  challengesLocked,
}: {
  artifact: ArtifactPlacementDescriptor
  descriptor: TowerArtifactAssetDescriptor | null
  piece: TowerLayoutPieceDescriptor
  pieceDescriptor: TowerPieceAssetDescriptor | null
  role: TowerArtifactRole
  storeyId: number
  adventures: CommandAdventureSummary[]
  tomes: TomeSummary[]
  challenges: ChallengeSummary[]
  challengesLocked: boolean
}) {
  const select = useTowerSelection((state) => state.select)
  const selected = useTowerSelection((state) => state.selected)
  const variant = piece.pieceType === 'section' && role !== 'normal' ? role : pieceVariant(null, piece)
  const staticArtifact = (
    <TowerArtifact
      artifact={artifact}
      descriptor={descriptor}
      pieceDescriptor={pieceDescriptor}
      pieceVariant={variant}
    />
  )

  if (role === 'adventure') {
    const adventure = findContent(adventures, artifact.contentBinding?.id)
    if (!adventure) return staticArtifact
    const isCurrent = isSelected(selected, { kind: 'adventure', storeyId, adventure })
    return (
      <TowerArtifact
        artifact={artifact}
        descriptor={descriptor}
        pieceDescriptor={pieceDescriptor}
        pieceVariant={variant}
        interactive
        selected={isCurrent}
        label={`Select Command Adventure: ${adventure.title}`}
        onClick={() => select({ kind: 'adventure', storeyId, adventure })}
      />
    )
  }

  if (role === 'tome') {
    const tome = findContent(tomes, artifact.contentBinding?.id)
    if (!tome) return staticArtifact
    const isCurrent = isSelected(selected, { kind: 'tome', storeyId, tome })
    return (
      <TowerArtifact
        artifact={artifact}
        descriptor={descriptor}
        pieceDescriptor={pieceDescriptor}
        pieceVariant={variant}
        interactive
        selected={isCurrent}
        label={`Select Tome: ${tome.title}`}
        onClick={() => select({ kind: 'tome', storeyId, tome })}
      />
    )
  }

  if (role === 'challenge') {
    const challenge = findContent(challenges, artifact.contentBinding?.id)
    if (!challenge) return staticArtifact
    const level = challengeLevelForArtifact(challenge, artifact.contentBinding, challengesLocked)
    if (!level) return staticArtifact
    const challengeIndex = challenges.findIndex((item) => item.id === challenge.id)
    const isCurrent = isSelected(selected, {
      kind: 'challenge',
      storeyId,
      challengeIndex,
      challenge,
      level,
      locked: challengesLocked || level.status === 'locked',
    })
    const accent = challengeLevelAccent(level)
    return (
      <TowerArtifact
        artifact={artifact}
        descriptor={descriptor}
        pieceDescriptor={pieceDescriptor}
        pieceVariant={variant}
        interactive
        selected={isCurrent}
        locked={challengesLocked || level.status === 'locked'}
        accent={accent}
        label={`Select ${challenge.title}: ${difficultyLabel(level)}`}
        onClick={() =>
          select({
            kind: 'challenge',
            storeyId,
            challengeIndex,
            challenge,
            level,
            locked: challengesLocked || level.status === 'locked',
          })
        }
      />
    )
  }

  return staticArtifact
}

function preferredChallengeLevel(levels: ChallengeLevelAccess[], locked: boolean) {
  if (!levels.length) return null
  if (locked) return levels[0]
  return (
    levels.find((level) => level.status === 'in_progress') ??
    levels.find((level) => level.status === 'not_started' || level.status === 'failed' || level.status === 'abandoned') ??
    levels.find((level) => level.status !== 'locked') ??
    levels[0]
  )
}

function challengeLevelForArtifact(
  challenge: ChallengeSummary,
  binding: ArtifactPlacementDescriptor['contentBinding'] | undefined | null,
  locked: boolean,
) {
  const boundLevel =
    binding?.levelId !== undefined
      ? challenge.levels.find((level) => String(level.id) === String(binding.levelId))
      : binding?.difficulty
        ? challenge.levels.find((level) => String(level.difficulty) === String(binding.difficulty))
        : null
  return boundLevel ?? preferredChallengeLevel(challenge.levels, locked)
}

function findContent<T extends { id: number | string }>(items: T[], id: number | string | undefined) {
  if (id === undefined) return null
  return items.find((item) => String(item.id) === String(id)) ?? null
}

function firstInteractableRole(artifacts: ArtifactPlacementDescriptor[]): TowerArtifactRole {
  return artifacts.find((artifact) => artifact.role !== 'normal')?.role ?? 'normal'
}

function groupArtifacts(artifacts: ArtifactPlacementDescriptor[]) {
  const map = new Map<string, ArtifactPlacementDescriptor[]>()
  for (const artifact of artifacts) {
    const list = map.get(artifact.targetInstanceId) ?? []
    list.push(artifact)
    map.set(artifact.targetInstanceId, list)
  }
  return map
}

export const TowerStoreySection = memo(TowerStoreySectionInner)
TowerStoreySection.displayName = 'TowerStoreySection'
