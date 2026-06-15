import { useState, type KeyboardEvent, type ReactNode } from 'react'
import { BookOpen, Swords, Trophy } from 'lucide-react'

import type { PaletteDragPayload } from '@/features/tower-designs/components/PiecePalette'
import { pieceIdFromInstance } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { PieceArt } from '@/features/tower-map/components/PieceArt'
import { RoofSpire, TomeLanding, TowerLanding, WindowStorey } from '@/features/tower-map/components/TowerStoreySection'
import {
  clientPointToPiecePoint,
  pieceByType,
  piecePointToCss,
  pieceVariant,
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
          const point = clientPointToPiecePoint(
            event.clientX,
            event.clientY,
            event.currentTarget as HTMLElement,
            descriptorFor(piece),
            variantForPiece(piece),
          )
          onPlaceArtifact(
            pieceId,
            payload.assetId,
            Math.round(point.x),
            Math.round(point.y),
          )
        }
      },
    }
  }

  function variantForPiece(piece: TowerLayoutPieceDescriptor) {
    return pieceVariant(layout, piece)
  }

  function artifactsFor(
    piece: TowerLayoutPieceDescriptor,
    pieceDescriptor: TowerPieceAssetDescriptor | null,
    variant?: string,
  ): ReactNode {
    const placements = artifactsByInstance.get(piece.instanceId)
    if (!placements?.length) return null
    return placements.map((artifact) => (
      <ArtifactOverlay
        key={artifact.id}
        artifact={artifact}
        artifactDescriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
        pieceDescriptor={pieceDescriptor}
        pieceVariant={variant}
        onMoveArtifact={onMoveArtifact}
      />
    ))
  }

  const spirePiece = pieceByType(layout, 'spire')
  const windowPiece = pieceByType(layout, 'window_section')
  const tomePiece = pieceByType(layout, 'tome')
  const adventurePiece = pieceByType(layout, 'adventure_section')
  const challengePiece = pieceByType(layout, 'challenge_section')
  // Landings are identified by the section they cap, not by instanceId — saved
  // designs use numeric `…-piece-<n>` ids that carry no semantic suffix.
  const landings = layout.pieces.filter((piece) => piece.pieceType === 'landing')
  const tomeLanding = landings.find((piece) => pieceVariant(layout, piece) === 'tome') ?? null
  const adventureLanding = landings.find((piece) => pieceVariant(layout, piece) === 'regular') ?? null
  const challengeLanding =
    landings.find((piece) => pieceVariant(layout, piece) === 'after-challenges') ?? null

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
            <RoofSpire
              animate={false}
              piece={spirePiece}
              descriptor={descriptorFor(spirePiece)}
              className={regionClass(pieceIdFromInstance(spirePiece.instanceId))}
              {...regionHandlers(spirePiece, pieceIdFromInstance(spirePiece.instanceId))}
            >
              {artifactsFor(spirePiece, descriptorFor(spirePiece), 'roof')}
            </RoofSpire>
          ) : null}

          {windowPiece ? (
            <WindowStorey
              animate={false}
              piece={windowPiece}
              descriptor={descriptorFor(windowPiece)}
              className={regionClass(pieceIdFromInstance(windowPiece.instanceId))}
              {...regionHandlers(windowPiece, pieceIdFromInstance(windowPiece.instanceId))}
            >
              {artifactsFor(windowPiece, descriptorFor(windowPiece), 'regular')}
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
              {artifactsFor(tomePiece, descriptorFor(tomePiece))}
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
              {artifactsFor(tomeLanding, descriptorFor(tomeLanding), 'tome')}
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
              {artifactsFor(adventurePiece, descriptorFor(adventurePiece), 'adventure')}
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
              {artifactsFor(adventureLanding, descriptorFor(adventureLanding), 'regular')}
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
              {artifactsFor(challengePiece, descriptorFor(challengePiece), 'challenge')}
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
              {artifactsFor(challengeLanding, descriptorFor(challengeLanding), 'after-challenges')}
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
    Icon: Swords,
  },
  challenge: {
    stageClass: 'tower-challenges-stage',
    iconClass: 'tower-stage-icon--purple',
    titleClass: 'tower-stage-title--challenge',
    title: 'Challenges',
    Icon: Trophy,
  },
  tome: {
    stageClass: 'tower-tome-stage',
    iconClass: 'tower-stage-icon--cyan',
    titleClass: 'tower-stage-title--tome',
    title: 'Tome',
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
  const { stageClass, iconClass, titleClass, title, Icon } = STAGE_SHELL[kind]
  return (
    <section
      className={cn(stageClass, className)}
      {...towerPieceAttrs(piece, descriptor, { variant: kind })}
      {...handlers}
    >
      <PieceArt pieceType={piece.pieceType} descriptor={descriptor} variant={kind} />
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
  artifactDescriptor,
  pieceDescriptor,
  pieceVariant,
  onMoveArtifact,
}: {
  artifact: ArtifactPlacementDescriptor
  artifactDescriptor: TowerArtifactAssetDescriptor | null
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  onMoveArtifact: (placementId: number, x: number, y: number) => void
}) {
  const sprite = artifactDescriptor?.sprites.default ?? (artifactDescriptor ? Object.values(artifactDescriptor.sprites)[0] : null)

  function onPointerDown(event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    // Coords are stored relative to the host piece; find it via the data marker
    // both render paths stamp, so no React ref into the reused piece is needed.
    const host = (event.currentTarget as HTMLElement).closest('[data-piece-id]')
    if (!(host instanceof HTMLElement)) return
    const hostEl: HTMLElement = host
    function move(ev: PointerEvent) {
      const point = clientPointToPiecePoint(ev.clientX, ev.clientY, hostEl, pieceDescriptor, pieceVariant)
      onMoveArtifact(artifact.id, Math.round(point.x), Math.round(point.y))
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
        ...piecePointToCss(artifact.x, artifact.y, pieceDescriptor, pieceVariant),
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
