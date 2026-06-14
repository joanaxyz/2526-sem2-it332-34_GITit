import { useState, type KeyboardEvent, type ReactNode } from 'react'
import { BookOpen, Swords, Trophy } from 'lucide-react'

import type { PaletteDragPayload } from '@/features/tower-designs/components/PiecePalette'
import { pieceIdFromInstance } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import {
  AdventureSectionPiece,
  ChallengeSectionPiece,
  TomePiece,
} from '@/features/tower-map/components/TowerPieces'
import { TomeLanding, TowerLanding, WindowStorey } from '@/features/tower-map/components/TowerStoreySection'
import {
  pieceByType,
  pieceBySuffix,
  towerDescriptorFor,
  towerPieceAttrs,
} from '@/features/tower-map/components/towerPieceData'
import type {
  TowerArtifactAssetDescriptor,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { backendUrl } from '@/shared/api/httpClient'
import { cn } from '@/shared/utils/cn'

/**
 * The editor canvas: ONE representative storey (the body repeats up the tower)
 * plus the crowning spire/roof. It renders the *real* tower piece components and
 * `tower-*` CSS — the same building blocks the live `/tower` view uses — so the
 * canvas reads as the actual tower, just static (no entrance animation) and with
 * the pieces made selectable/droppable. Editing this one storey edits every
 * repeat, because the live tower reuses the same shared layout template.
 */
export function EditorStorey({
  overview,
  pieceDescriptorBySlug,
  pieceDescriptorById,
  artifactDescriptorBySlug,
  selectedPieceId,
  pendingSwaps,
  onSelectPiece,
  onSwapAsset,
  onPlaceArtifact,
  onMoveArtifact,
  onOpenSection,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  pieceDescriptorById: Map<number, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  /** pieceId → asset id chosen but not yet committed; previewed live on the canvas. */
  pendingSwaps: Map<number, number>
  onSelectPiece: (pieceId: number) => void
  onSwapAsset: (pieceId: number, assetId: number) => void
  onPlaceArtifact: (pieceId: number, assetId: number, x: number, y: number) => void
  onMoveArtifact: (placementId: number, x: number, y: number) => void
  /** Double-click / Shift+Enter on a piece opens the focused section editor. */
  onOpenSection?: (pieceId: number) => void
}) {
  const layout = overview.tower_layout
  const artifactsByInstance = groupArtifacts(overview.artifacts)

  // A pending pick previews live: render the chosen asset in the slot instead of
  // the committed one. Apply (in the toolbar) is what actually persists it.
  function descriptorFor(piece: TowerLayoutPieceDescriptor): TowerPieceAssetDescriptor | null {
    const pieceId = pieceIdFromInstance(piece.instanceId)
    if (pieceId !== null) {
      const previewAssetId = pendingSwaps.get(pieceId)
      if (previewAssetId !== undefined) return pieceDescriptorById.get(previewAssetId) ?? null
    }
    return towerDescriptorFor(piece, pieceDescriptorBySlug)
  }

  const [dropHoverId, setDropHoverId] = useState<number | null>(null)
  const [rejectedId, setRejectedId] = useState<number | null>(null)

  function flashReject(pieceId: number) {
    setRejectedId(pieceId)
    window.setTimeout(() => setRejectedId((id) => (id === pieceId ? null : id)), 1100)
  }

  // The base `editor-piece` marker lets the zoom/pan handler ignore grabs that
  // land on a piece (only the sky pans); the modifiers paint editor feedback.
  function regionClass(pieceId: number | null): string {
    return cn(
      'editor-piece',
      pieceId !== null && pieceId === selectedPieceId && 'editor-piece--selected',
      pieceId !== null && pendingSwaps.has(pieceId) && 'editor-piece--pending',
      pieceId !== null && pieceId === dropHoverId && 'editor-piece--drop',
      pieceId !== null && pieceId === rejectedId && 'editor-piece--reject',
    )
  }

  function regionHandlers(piece: TowerLayoutPieceDescriptor, pieceId: number | null) {
    if (pieceId === null) return {}
    return {
      role: 'button' as const,
      tabIndex: 0,
      'aria-pressed': pieceId === selectedPieceId,
      'aria-label': `${piece.pieceType} piece`,
      onClick: () => onSelectPiece(pieceId),
      onDoubleClick: () => onOpenSection?.(pieceId),
      onKeyDown: (event: KeyboardEvent) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          if (event.shiftKey) onOpenSection?.(pieceId)
          else onSelectPiece(pieceId)
        }
      },
      onDragOver: (event: React.DragEvent) => {
        event.preventDefault()
        event.dataTransfer.dropEffect = 'copy'
        setDropHoverId(pieceId)
      },
      onDragLeave: () => setDropHoverId((id) => (id === pieceId ? null : id)),
      onDrop: (event: React.DragEvent) => {
        event.preventDefault()
        setDropHoverId(null)
        const payload = readDrag(event)
        if (!payload) return
        if (payload.source === 'palette-piece') {
          if (payload.pieceType === piece.pieceType) onSwapAsset(pieceId, payload.assetId)
          else flashReject(pieceId)
          return
        }
        if (payload.source === 'palette-artifact') {
          const rect = event.currentTarget.getBoundingClientRect()
          onPlaceArtifact(
            pieceId,
            payload.assetId,
            Math.round(event.clientX - rect.left),
            Math.round(event.clientY - rect.top),
          )
        }
      },
    }
  }

  function artifactsFor(instanceId: string): ReactNode {
    const placements = artifactsByInstance.get(instanceId)
    if (!placements?.length) return null
    return placements.map((artifact) => (
      <ArtifactOverlay
        key={artifact.id}
        artifact={artifact}
        descriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
        onMoveArtifact={onMoveArtifact}
      />
    ))
  }

  const spirePiece = pieceByType(layout, 'spire')
  const tomePiece = pieceByType(layout, 'tome')
  const tomeLanding = pieceBySuffix(layout, 'landing-after-tomes')
  const adventurePiece = pieceByType(layout, 'adventure_section')
  const adventureLanding =
    pieceBySuffix(layout, 'landing-after-adventure') ?? pieceByType(layout, 'landing')
  const challengePiece = pieceByType(layout, 'challenge_section')
  const challengeLanding = pieceBySuffix(layout, 'landing-after-challenges')

  if (layout.pieces.length === 0) {
    return (
      <div className="editor-stage" aria-label="Tower editor canvas">
        <p className="editor-empty">This tower has no pieces yet.</p>
      </div>
    )
  }

  return (
    <div className="editor-stage" aria-label="Tower editor canvas">
      <p className="editor-stage-kicker">A storey repeats up the tower — design it once.</p>
      <div className="learning-tower">
        <div className="tower-repeater">
          {spirePiece ? (
            <WindowStorey
              animate={false}
              crowned
              piece={spirePiece}
              descriptor={descriptorFor(spirePiece)}
              className={regionClass(pieceIdFromInstance(spirePiece.instanceId))}
              {...regionHandlers(spirePiece, pieceIdFromInstance(spirePiece.instanceId))}
            >
              {artifactsFor(spirePiece.instanceId)}
            </WindowStorey>
          ) : null}

          {tomePiece ? (
            <StageShell
              kind="tome"
              piece={tomePiece}
              descriptor={descriptorFor(tomePiece)}
              className={regionClass(pieceIdFromInstance(tomePiece.instanceId))}
              handlers={regionHandlers(tomePiece, pieceIdFromInstance(tomePiece.instanceId))}
            >
              {artifactsFor(tomePiece.instanceId)}
            </StageShell>
          ) : null}

          {tomeLanding ? (
            <TomeLanding
              animate={false}
              piece={tomeLanding}
              descriptor={descriptorFor(tomeLanding)}
              className={regionClass(pieceIdFromInstance(tomeLanding.instanceId))}
              {...regionHandlers(tomeLanding, pieceIdFromInstance(tomeLanding.instanceId))}
            >
              {artifactsFor(tomeLanding.instanceId)}
            </TomeLanding>
          ) : null}

          {adventurePiece ? (
            <StageShell
              kind="adventure"
              piece={adventurePiece}
              descriptor={descriptorFor(adventurePiece)}
              className={regionClass(pieceIdFromInstance(adventurePiece.instanceId))}
              handlers={regionHandlers(adventurePiece, pieceIdFromInstance(adventurePiece.instanceId))}
            >
              {artifactsFor(adventurePiece.instanceId)}
            </StageShell>
          ) : null}

          {adventureLanding ? (
            <TowerLanding
              animate={false}
              piece={adventureLanding}
              descriptor={descriptorFor(adventureLanding)}
              className={regionClass(pieceIdFromInstance(adventureLanding.instanceId))}
              {...regionHandlers(adventureLanding, pieceIdFromInstance(adventureLanding.instanceId))}
            >
              {artifactsFor(adventureLanding.instanceId)}
            </TowerLanding>
          ) : null}

          {challengePiece ? (
            <StageShell
              kind="challenge"
              piece={challengePiece}
              descriptor={descriptorFor(challengePiece)}
              className={regionClass(pieceIdFromInstance(challengePiece.instanceId))}
              handlers={regionHandlers(challengePiece, pieceIdFromInstance(challengePiece.instanceId))}
            >
              {artifactsFor(challengePiece.instanceId)}
            </StageShell>
          ) : null}

          {challengeLanding ? (
            <TowerLanding
              animate={false}
              afterChallenges
              base
              piece={challengeLanding}
              descriptor={descriptorFor(challengeLanding)}
              className={regionClass(pieceIdFromInstance(challengeLanding.instanceId))}
              {...regionHandlers(challengeLanding, pieceIdFromInstance(challengeLanding.instanceId))}
            >
              {artifactsFor(challengeLanding.instanceId)}
            </TowerLanding>
          ) : null}
        </div>
      </div>
    </div>
  )
}

const STAGE_SHELL = {
  adventure: {
    stageClass: 'tower-adventure-stage',
    iconClass: 'tower-stage-icon--cyan',
    titleClass: 'tower-stage-title--adventure',
    title: 'Command Adventure',
    Art: AdventureSectionPiece,
    Icon: Swords,
  },
  challenge: {
    stageClass: 'tower-challenges-stage',
    iconClass: 'tower-stage-icon--purple',
    titleClass: 'tower-stage-title--challenge',
    title: 'Challenges',
    Art: ChallengeSectionPiece,
    Icon: Trophy,
  },
  tome: {
    stageClass: 'tower-tome-stage',
    iconClass: 'tower-stage-icon--cyan',
    titleClass: 'tower-stage-title--tome',
    title: 'Tome',
    Art: TomePiece,
    Icon: BookOpen,
  },
} as const

// The neon stage shell (background piece + icon + title), drawn with the real
// `tower-*-stage` classes so it matches the live tower exactly. Content (live
// doors/trials/lecterns) is a live-view concern, so the editor leaves it empty.
function StageShell({
  kind,
  piece,
  descriptor,
  className,
  handlers,
  children,
}: {
  kind: 'adventure' | 'challenge' | 'tome'
  piece: TowerLayoutPieceDescriptor
  descriptor: TowerPieceAssetDescriptor | null
  className: string
  handlers: Record<string, unknown>
  children?: ReactNode
}) {
  const { stageClass, iconClass, titleClass, title, Art, Icon } = STAGE_SHELL[kind]
  return (
    <section className={cn(stageClass, className)} {...towerPieceAttrs(piece, descriptor)} {...handlers}>
      <Art descriptor={descriptor} />
      <span className={cn('tower-stage-icon', iconClass)}>
        <Icon className="size-6" />
      </span>
      <h2 className={cn('tower-stage-title', titleClass)}>{title}</h2>
      {children}
    </section>
  )
}

function ArtifactOverlay({
  artifact,
  descriptor,
  onMoveArtifact,
}: {
  artifact: ArtifactPlacementDescriptor
  descriptor: TowerArtifactAssetDescriptor | null
  onMoveArtifact: (placementId: number, x: number, y: number) => void
}) {
  const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)

  function onPointerDown(event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    // Coords are stored relative to the host piece; find it via the data marker
    // both render paths stamp, so no React ref into the reused piece is needed.
    const host = (event.currentTarget as HTMLElement).closest('[data-piece-id]')
    const rect = host?.getBoundingClientRect()
    if (!rect) return
    const { left, top } = rect
    function move(ev: PointerEvent) {
      onMoveArtifact(artifact.id, Math.round(ev.clientX - left), Math.round(ev.clientY - top))
    }
    function up() {
      window.removeEventListener('pointermove', move)
      window.removeEventListener('pointerup', up)
    }
    window.addEventListener('pointermove', move)
    window.addEventListener('pointerup', up)
  }

  return (
    <span
      className="editor-artifact"
      style={{
        left: `${artifact.x}px`,
        top: `${artifact.y}px`,
        transform: `translate(-50%, -50%) scale(${artifact.scale}) rotate(${artifact.rotation}deg)`,
        zIndex: artifact.zIndex,
      }}
      onPointerDown={onPointerDown}
    >
      {sprite?.url ? <img src={backendUrl(sprite.url)} alt="" draggable={false} /> : null}
    </span>
  )
}

function readDrag(event: React.DragEvent): PaletteDragPayload | null {
  try {
    return JSON.parse(event.dataTransfer.getData('application/json')) as PaletteDragPayload
  } catch {
    return null
  }
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
