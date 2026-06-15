import { type ReactNode, useMemo, useState } from 'react'

import { pieceIdFromInstance } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { RoofSpire, TowerLanding, TowerSectionShell } from '@/features/tower-map/components/TowerStoreySection'
import { TowerArtifact } from '@/features/tower-map/components/TowerArtifact'
import {
  clientPointToPiecePoint,
  pieceVariant,
  towerDescriptorFor,
} from '@/features/tower-map/components/towerPieceData'
import type {
  TowerArtifactAssetDescriptor,
  TowerArtifactRole,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

export type EditorDragPayload =
  | { source: 'asset-piece'; assetId: number; slug: string; pieceType: string }
  | {
      source: 'asset-artifact'
      assetId: number
      slug: string
      role: TowerArtifactRole
      contentDefinitionId?: number | null
    }

export type PlacementDraft = Extract<EditorDragPayload, { source: 'asset-artifact' }> | null

export function EditorStorey({
  overview,
  pieceDescriptorBySlug,
  pieceDescriptorById,
  artifactDescriptorBySlug,
  selectedPieceId,
  pendingSwaps,
  placementDraft,
  storeyIndex,
  onSelectPiece,
  onSwapAsset,
  onPlaceArtifact,
  onMoveArtifact,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  pieceDescriptorById: Map<number, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  pendingSwaps: Map<number, number>
  placementDraft: PlacementDraft
  storeyIndex?: number | null
  onSelectPiece: (pieceId: number) => void
  onSwapAsset: (pieceId: number, assetId: number) => void
  onPlaceArtifact: (
    pieceId: number,
    assetId: number,
    role: TowerArtifactRole,
    contentDefinitionId: number | null | undefined,
    x: number,
    y: number,
  ) => void
  onMoveArtifact: (placementId: number | string, x: number, y: number) => void
}) {
  const layout = overview.tower_layout
  const artifactsByInstance = useMemo(() => groupArtifacts(overview.artifacts), [overview.artifacts])
  const [dropHoverId, setDropHoverId] = useState<number | null>(null)
  const [rejectedId, setRejectedId] = useState<number | null>(null)

  function descriptorFor(piece: TowerLayoutPieceDescriptor): TowerPieceAssetDescriptor | null {
    const pieceId = pieceIdFromInstance(piece.instanceId)
    if (pieceId !== null) {
      const previewAssetId = pendingSwaps.get(pieceId)
      if (previewAssetId !== undefined) return pieceDescriptorById.get(previewAssetId) ?? null
    }
    return towerDescriptorFor(piece, pieceDescriptorBySlug)
  }

  function flashReject(pieceId: number) {
    setRejectedId(pieceId)
    window.setTimeout(() => setRejectedId((id) => (id === pieceId ? null : id)), 900)
  }

  function regionClass(pieceId: number | null): string {
    return cn(
      'editor-piece',
      pieceId !== null && pieceId === selectedPieceId && 'editor-piece--selected',
      pieceId !== null && pendingSwaps.has(pieceId) && 'editor-piece--pending',
      pieceId !== null && pieceId === dropHoverId && 'editor-piece--drop',
      pieceId !== null && pieceId === rejectedId && 'editor-piece--reject',
    )
  }

  function canPlaceArtifact(piece: TowerLayoutPieceDescriptor, payload: PlacementDraft) {
    if (!payload) return false
    if (payload.role === 'normal') return true
    return piece.pieceType === 'section'
  }

  function placePayloadOnPiece(
    piece: TowerLayoutPieceDescriptor,
    payload: PlacementDraft,
    target: HTMLElement,
    clientX: number,
    clientY: number,
  ) {
    const pieceId = pieceIdFromInstance(piece.instanceId)
    if (pieceId === null || !payload) return
    if (!canPlaceArtifact(piece, payload)) {
      flashReject(pieceId)
      return
    }
    const point = clientPointToPiecePoint(clientX, clientY, target, descriptorFor(piece), variantForPiece(piece))
    onPlaceArtifact(
      pieceId,
      payload.assetId,
      payload.role,
      payload.contentDefinitionId,
      Math.round(point.x),
      Math.round(point.y),
    )
  }

  function regionHandlers(piece: TowerLayoutPieceDescriptor, pieceId: number | null) {
    if (pieceId === null) return {}
    return {
      role: 'button' as const,
      tabIndex: 0,
      'aria-pressed': pieceId === selectedPieceId,
      'aria-label': `${piece.pieceType} piece`,
      onClick: (event: React.MouseEvent<HTMLElement>) => {
        if (placementDraft) {
          placePayloadOnPiece(piece, placementDraft, event.currentTarget, event.clientX, event.clientY)
          return
        }
        onSelectPiece(pieceId)
      },
      onKeyDown: (event: React.KeyboardEvent) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onSelectPiece(pieceId)
        }
      },
      onDragOver: (event: React.DragEvent) => {
        event.preventDefault()
        event.dataTransfer.dropEffect = 'copy'
        setDropHoverId(pieceId)
      },
      onDragLeave: () => setDropHoverId((id) => (id === pieceId ? null : id)),
      onDrop: (event: React.DragEvent<HTMLElement>) => {
        event.preventDefault()
        setDropHoverId(null)
        const payload = readDrag(event)
        if (!payload) return
        if (payload.source === 'asset-piece') {
          if (payload.pieceType === piece.pieceType) onSwapAsset(pieceId, payload.assetId)
          else flashReject(pieceId)
          return
        }
        placePayloadOnPiece(piece, payload, event.currentTarget, event.clientX, event.clientY)
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
      <EditableArtifact
        key={artifact.id}
        artifact={artifact}
        artifactDescriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
        pieceDescriptor={pieceDescriptor}
        pieceVariant={variant}
        onMoveArtifact={onMoveArtifact}
      />
    ))
  }

  if (layout.pieces.length === 0) {
    return (
      <div className="tower-stack-column tower-stack-column--editor" aria-label="Tower editor canvas">
        <section className="storey-section storey-section--editor">
          <div className="learning-tower">
            <p className="editor-empty">This tower has no pieces yet.</p>
          </div>
        </section>
      </div>
    )
  }

  const pieces = visibleStoreyPieces(layout.pieces, storeyIndex)
  return (
    <div className="tower-stack-column tower-stack-column--editor" aria-label="Tower editor canvas">
      <section className="storey-section storey-section--editor">
        <div className="learning-tower">
          <div className="tower-repeater">
            {pieces.map((piece) => {
              const pieceId = pieceIdFromInstance(piece.instanceId)
              const descriptor = descriptorFor(piece)
              const artifacts = artifactsByInstance.get(piece.instanceId) ?? []
              const role = firstInteractableRole(artifacts)
              const handlers = regionHandlers(piece, pieceId)
              if (piece.pieceType === 'crown') {
                return (
                  <RoofSpire
                    key={piece.instanceId}
                    piece={piece}
                    descriptor={descriptor}
                    className={regionClass(pieceId)}
                    {...handlers}
                  >
                    {artifactsFor(piece, descriptor, 'roof')}
                  </RoofSpire>
                )
              }
              if (piece.pieceType === 'landing') {
                const variant = variantForPiece(piece)
                return (
                  <TowerLanding
                    key={piece.instanceId}
                    variant={variant}
                    piece={piece}
                    descriptor={descriptor}
                    className={regionClass(pieceId)}
                    {...handlers}
                  >
                    {artifactsFor(piece, descriptor, variant)}
                  </TowerLanding>
                )
              }
              return (
                <TowerSectionShell
                  key={piece.instanceId}
                  artifactRole={role}
                  piece={piece}
                  descriptor={descriptor}
                  className={regionClass(pieceId)}
                  {...handlers}
                >
                  {artifactsFor(piece, descriptor, role)}
                </TowerSectionShell>
              )
            })}
          </div>
        </div>
      </section>
    </div>
  )
}

function EditableArtifact({
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
  onMoveArtifact: (placementId: number | string, x: number, y: number) => void
}) {
  function onPointerDown(event: React.PointerEvent<HTMLElement>) {
    event.stopPropagation()
    event.preventDefault()
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
    <TowerArtifact
      artifact={artifact}
      descriptor={artifactDescriptor}
      pieceDescriptor={pieceDescriptor}
      pieceVariant={pieceVariant}
      onPointerDown={onPointerDown}
      className="editor-artifact"
    />
  )
}

function readDrag(event: React.DragEvent): EditorDragPayload | null {
  try {
    return JSON.parse(event.dataTransfer.getData('application/json')) as EditorDragPayload
  } catch {
    return null
  }
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

function visibleStoreyPieces(pieces: TowerLayoutPieceDescriptor[], storeyIndex: number | null | undefined) {
  const nonCrown = pieces.filter((piece) => piece.pieceType !== 'crown')
  const fallbackIndex = normalizedStoreyIndex(nonCrown[0])
  const activeIndex = storeyIndex ?? fallbackIndex
  const crown =
    pieces.find((piece) => piece.pieceType === 'crown' && normalizedStoreyIndex(piece) === activeIndex) ??
    pieces.find((piece) => piece.pieceType === 'crown') ??
    null
  const storeyPieces = nonCrown.filter((piece) => normalizedStoreyIndex(piece) === activeIndex)
  return crown ? [crown, ...storeyPieces] : storeyPieces
}

function normalizedStoreyIndex(piece: TowerLayoutPieceDescriptor | undefined | null) {
  return typeof piece?.storeyIndex === 'number' ? piece.storeyIndex : 0
}
