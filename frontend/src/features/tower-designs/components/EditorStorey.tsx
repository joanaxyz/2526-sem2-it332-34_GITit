import { type CSSProperties, type ReactNode, useMemo, useState } from 'react'
import { RotateCw } from 'lucide-react'

import {
  type ArtifactEdit,
  type ArtifactTransform,
  ARTIFACT_ROTATION_RANGE,
  ARTIFACT_SCALE_RANGE,
  type PieceTransform,
  PIECE_ROTATION_RANGE,
  PIECE_SCALE_RANGE,
  clampNumber,
  pieceIdFromInstance,
  pieceTransformToRecord,
  readArtifactTransform,
  readPieceTransform,
  roundTo,
} from '@/features/tower-designs/editorUtils'
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
  selectedArtifactId,
  pendingSwaps,
  pieceTransforms,
  artifactEdits,
  zoomScale,
  placementDraft,
  onSelectPiece,
  onSelectArtifact,
  onSwapAsset,
  onPlaceArtifact,
  onMoveArtifact,
  onTransformArtifact,
  onTransformPiece,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  pieceDescriptorById: Map<number, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  selectedArtifactId: number | string | null
  pendingSwaps: Map<number, number>
  pieceTransforms: Map<number, PieceTransform>
  artifactEdits: Map<number | string, ArtifactEdit>
  zoomScale: number
  placementDraft: PlacementDraft
  onSelectPiece: (pieceId: number) => void
  onSelectArtifact: (artifactId: number | string, pieceId: number | null) => void
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
  onTransformArtifact: (placementId: number | string, next: ArtifactTransform) => void
  onTransformPiece: (pieceId: number, next: PieceTransform) => void
}) {
  const layout = overview.tower_layout
  const artifactsByInstance = useMemo(() => groupArtifacts(overview.artifacts), [overview.artifacts])
  const [dropHoverId, setDropHoverId] = useState<number | null>(null)
  const [rejectedId, setRejectedId] = useState<number | null>(null)

  function descriptorFor(piece: TowerLayoutPieceDescriptor): TowerPieceAssetDescriptor | null {
    const pieceId = pieceIdFromInstance(piece.instanceId)
    if (pieceId !== null) {
      const stagedAssetId = pendingSwaps.get(pieceId)
      if (stagedAssetId !== undefined) return pieceDescriptorById.get(stagedAssetId) ?? null
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
    if (piece.pieceType !== 'section') return false
    const artifacts = artifactsByInstance.get(piece.instanceId) ?? []
    const interactables = artifacts.filter((artifact) => artifact.role !== 'normal')
    if (payload.role === 'challenge') {
      return interactables.every((artifact) => artifact.role === 'challenge') && interactables.length < 3
    }
    return interactables.length === 0
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
        const payload = readDrag(event)
        const canDrop =
          payload?.source === 'asset-piece'
            ? payload.pieceType === piece.pieceType
            : payload?.source === 'asset-artifact'
              ? canPlaceArtifact(piece, payload)
              : false
        event.dataTransfer.dropEffect = canDrop ? 'copy' : 'none'
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
    pieceId?: number | null,
  ): ReactNode {
    const placements = artifactsByInstance.get(piece.instanceId)
    if (!placements?.length) return null
    return placements.map((artifact) => {
      const edit = artifactEdits.get(artifact.id)
      const transformed = readArtifactTransform(artifact, edit)
      const selected = selectedArtifactId === artifact.id
      return (
        <EditableArtifact
          key={artifact.id}
          artifact={{
            ...artifact,
            ...transformed,
            zIndex: selected ? 100000 : artifact.zIndex,
          }}
          artifactDescriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
          pieceDescriptor={pieceDescriptor}
          pieceVariant={variant}
          selected={selected}
          zoomScale={zoomScale}
          onSelectArtifact={() => onSelectArtifact(artifact.id, pieceId ?? null)}
          onMoveArtifact={onMoveArtifact}
          onTransformArtifact={(next) => onTransformArtifact(artifact.id, next)}
        />
      )
    })
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

  const { crown, storeys } = editorTowerPieces(layout.pieces)
  const renderPiece = (piece: TowerLayoutPieceDescriptor) => {
    const pieceId = pieceIdFromInstance(piece.instanceId)
    const descriptor = descriptorFor(piece)
    const artifacts = artifactsByInstance.get(piece.instanceId) ?? []
    const role = firstInteractableRole(artifacts)
    const handlers = regionHandlers(piece, pieceId)
    // The visible transform is the staged override (live edit) layered over the
    // committed server value, so the canvas reflects unsaved tweaks instantly.
    const staged = pieceId !== null ? pieceTransforms.get(pieceId) : undefined
    const effective = staged ?? readPieceTransform(piece.transform)
    const renderedPiece = staged ? { ...piece, transform: pieceTransformToRecord(staged) } : piece
    const showFrame = pieceId !== null && pieceId === selectedPieceId && !placementDraft
    const frame = showFrame ? (
      <PieceTransformFrame
        transform={effective}
        zoomScale={zoomScale}
        onChange={(next) => onTransformPiece(pieceId as number, next)}
      />
    ) : null

    if (piece.pieceType === 'crown') {
      return (
        <RoofSpire
          key={piece.instanceId}
          piece={renderedPiece}
          descriptor={descriptor}
          className={regionClass(pieceId)}
          {...handlers}
        >
          {frame}
          {artifactsFor(piece, descriptor, 'roof', pieceId)}
        </RoofSpire>
      )
    }
    if (piece.pieceType === 'landing') {
      const variant = variantForPiece(piece)
      return (
        <TowerLanding
          key={piece.instanceId}
          variant={variant}
          piece={renderedPiece}
          descriptor={descriptor}
          className={regionClass(pieceId)}
          {...handlers}
        >
          {frame}
          {artifactsFor(piece, descriptor, variant, pieceId)}
        </TowerLanding>
      )
    }
    return (
      <TowerSectionShell
        key={piece.instanceId}
        artifactRole={role}
        piece={renderedPiece}
        descriptor={descriptor}
        className={regionClass(pieceId)}
        {...handlers}
      >
        {frame}
        {artifactsFor(piece, descriptor, role, pieceId)}
      </TowerSectionShell>
    )
  }

  return (
    <div className="tower-stack-column tower-stack-column--editor" aria-label="Tower editor canvas">
      <section className="storey-section storey-section--editor">
        <div className="learning-tower">
          <div className="tower-repeater">
            {crown ? renderPiece(crown) : null}
            {storeys.map((group, order) => (
              <div className="editor-storey-band" key={group.storeyIndex} aria-label={`Storey ${order + 1}`}>
                {group.pieces.map(renderPiece)}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

/**
 * The on-canvas transform gizmo for the selected piece. It lives INSIDE the
 * piece element, so it inherits the piece's translate/scale/rotate and stays
 * glued to the art. Dragging the body moves; corner handles scale uniformly
 * around the centre; the top handle rotates. Edits are staged (no network) and
 * only committed when the user applies; see InTowerEditor.
 */
function PieceTransformFrame({
  transform,
  zoomScale,
  onChange,
}: {
  transform: PieceTransform
  zoomScale: number
  onChange: (next: PieceTransform) => void
}) {
  function centreOf(target: HTMLElement) {
    const host = (target.closest('[data-piece-id]') as HTMLElement | null) ?? target
    const rect = host.getBoundingClientRect()
    return { cx: rect.left + rect.width / 2, cy: rect.top + rect.height / 2 }
  }

  function beginMove(event: React.PointerEvent<HTMLDivElement>) {
    // Only the frame body moves; clicks that land on a handle are theirs.
    if (event.target !== event.currentTarget) return
    event.stopPropagation()
    event.preventDefault()
    const start = transform
    const startX = event.clientX
    const startY = event.clientY
    const z = zoomScale || 1
    trackPointer((moveEvent) => {
      const dx = (moveEvent.clientX - startX) / z
      const dy = (moveEvent.clientY - startY) / z
      onChange({ ...start, x: Math.round(start.x + dx), y: Math.round(start.y + dy) })
    })
  }

  function beginScale(event: React.PointerEvent<HTMLSpanElement>) {
    event.stopPropagation()
    event.preventDefault()
    const start = transform
    const { cx, cy } = centreOf(event.currentTarget)
    const startDistance = Math.hypot(event.clientX - cx, event.clientY - cy) || 1
    trackPointer((moveEvent) => {
      const distance = Math.hypot(moveEvent.clientX - cx, moveEvent.clientY - cy)
      const scale = clampNumber(
        roundTo(start.scale * (distance / startDistance), 2),
        PIECE_SCALE_RANGE.min,
        PIECE_SCALE_RANGE.max,
      )
      onChange({ ...start, scale })
    })
  }

  function beginRotate(event: React.PointerEvent<HTMLSpanElement>) {
    event.stopPropagation()
    event.preventDefault()
    const start = transform
    const { cx, cy } = centreOf(event.currentTarget)
    const startAngle = Math.atan2(event.clientY - cy, event.clientX - cx)
    trackPointer((moveEvent) => {
      const angle = Math.atan2(moveEvent.clientY - cy, moveEvent.clientX - cx)
      const rotation = clampNumber(
        Math.round(start.rotation + ((angle - startAngle) * 180) / Math.PI),
        PIECE_ROTATION_RANGE.min,
        PIECE_ROTATION_RANGE.max,
      )
      onChange({ ...start, rotation })
    })
  }

  // Handles counter-scale by the piece's own scale so the grips stay a usable
  // size whether the piece is shrunk or blown up. (Canvas zoom still applies.)
  const style = { '--ed-inv': 1 / Math.max(transform.scale, 0.001) } as CSSProperties

  return (
    <div className="ed-tf" style={style} onPointerDown={beginMove} aria-hidden="true">
      <span className="ed-tf-handle ed-tf-handle--nw" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--ne" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--se" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--sw" onPointerDown={beginScale} />
      <span className="ed-tf-rotate" onPointerDown={beginRotate}>
        <RotateCw className="ed-tf-rotate-icon" aria-hidden="true" />
      </span>
    </div>
  )
}

function trackPointer(move: (event: PointerEvent) => void) {
  const up = () => {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
  }
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', up)
}

function EditableArtifact({
  artifact,
  artifactDescriptor,
  pieceDescriptor,
  pieceVariant,
  selected,
  zoomScale,
  onSelectArtifact,
  onMoveArtifact,
  onTransformArtifact,
}: {
  artifact: ArtifactPlacementDescriptor
  artifactDescriptor: TowerArtifactAssetDescriptor | null
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  selected: boolean
  zoomScale: number
  onSelectArtifact: () => void
  onMoveArtifact: (placementId: number | string, x: number, y: number) => void
  onTransformArtifact: (next: ArtifactTransform) => void
}) {
  function onPointerDown(event: React.PointerEvent<HTMLElement>) {
    event.stopPropagation()
    event.preventDefault()
    onSelectArtifact()
    const host = (event.currentTarget as HTMLElement).closest('.editor-piece')
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
      className={cn('editor-artifact', selected && 'is-selected')}
    >
      {selected ? (
        <ArtifactTransformFrame
          artifact={artifact}
          pieceDescriptor={pieceDescriptor}
          pieceVariant={pieceVariant}
          zoomScale={zoomScale}
          onChange={onTransformArtifact}
        />
      ) : null}
    </TowerArtifact>
  )
}

function ArtifactTransformFrame({
  artifact,
  pieceDescriptor,
  pieceVariant,
  zoomScale,
  onChange,
}: {
  artifact: ArtifactPlacementDescriptor
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  zoomScale: number
  onChange: (next: ArtifactTransform) => void
}) {
  const transform = readArtifactTransform(artifact)

  function hostPiece(target: HTMLElement) {
    return target.closest('.editor-piece') as HTMLElement | null
  }

  function beginMove(event: React.PointerEvent<HTMLDivElement>) {
    if (event.target !== event.currentTarget) return
    event.stopPropagation()
    event.preventDefault()
    const host = hostPiece(event.currentTarget)
    if (!host) return
    const startPoint = clientPointToPiecePoint(event.clientX, event.clientY, host, pieceDescriptor, pieceVariant)
    const start = transform
    trackPointer((moveEvent) => {
      const point = clientPointToPiecePoint(moveEvent.clientX, moveEvent.clientY, host, pieceDescriptor, pieceVariant)
      onChange({
        ...start,
        x: Math.round(start.x + point.x - startPoint.x),
        y: Math.round(start.y + point.y - startPoint.y),
      })
    })
  }

  function beginScale(event: React.PointerEvent<HTMLSpanElement>) {
    event.stopPropagation()
    event.preventDefault()
    const rect = (event.currentTarget.closest('.tower-artifact') as HTMLElement | null)?.getBoundingClientRect()
    if (!rect) return
    const start = transform
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const startDistance = Math.hypot(event.clientX - cx, event.clientY - cy) || 1
    trackPointer((moveEvent) => {
      const distance = Math.hypot(moveEvent.clientX - cx, moveEvent.clientY - cy)
      const scale = clampNumber(
        roundTo(start.scale * (distance / startDistance), 2),
        ARTIFACT_SCALE_RANGE.min,
        ARTIFACT_SCALE_RANGE.max,
      )
      onChange({ ...start, scale })
    })
  }

  function beginRotate(event: React.PointerEvent<HTMLSpanElement>) {
    event.stopPropagation()
    event.preventDefault()
    const rect = (event.currentTarget.closest('.tower-artifact') as HTMLElement | null)?.getBoundingClientRect()
    if (!rect) return
    const start = transform
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    const startAngle = Math.atan2(event.clientY - cy, event.clientX - cx)
    trackPointer((moveEvent) => {
      const angle = Math.atan2(moveEvent.clientY - cy, moveEvent.clientX - cx)
      const rotation = clampNumber(
        Math.round(start.rotation + ((angle - startAngle) * 180) / Math.PI),
        ARTIFACT_ROTATION_RANGE.min,
        ARTIFACT_ROTATION_RANGE.max,
      )
      onChange({ ...start, rotation })
    })
  }

  const style = { '--ed-inv': 1 / Math.max(transform.scale * zoomScale, 0.001) } as CSSProperties

  return (
    <div className="ed-tf ed-tf--artifact" style={style} onPointerDown={beginMove} aria-hidden="true">
      <span className="ed-tf-handle ed-tf-handle--nw" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--ne" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--se" onPointerDown={beginScale} />
      <span className="ed-tf-handle ed-tf-handle--sw" onPointerDown={beginScale} />
      <span className="ed-tf-rotate" onPointerDown={beginRotate}>
        <RotateCw className="ed-tf-rotate-icon" aria-hidden="true" />
      </span>
    </div>
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

function editorTowerPieces(pieces: TowerLayoutPieceDescriptor[]) {
  const crown = pieces.find((piece) => piece.pieceType === 'crown') ?? null
  const groups = new Map<number, TowerLayoutPieceDescriptor[]>()
  for (const piece of pieces) {
    if (piece.pieceType === 'crown') continue
    const storeyIndex = typeof piece.storeyIndex === 'number' ? piece.storeyIndex : 0
    const group = groups.get(storeyIndex) ?? []
    group.push(piece)
    groups.set(storeyIndex, group)
  }
  return {
    crown,
    storeys: [...groups.entries()]
      .sort(([a], [b]) => a - b)
      .map(([storeyIndex, storeyPieces]) => ({ storeyIndex, pieces: storeyPieces })),
  }
}
