import { type CSSProperties, type ReactNode, useMemo, useState } from 'react'
import { RotateCw } from 'lucide-react'

import {
  type ArtifactEdit,
  type ArtifactTransform,
  ARTIFACT_ROTATION_RANGE,
  type PieceTransform,
  PIECE_ROTATION_RANGE,
  PIECE_SCALE_RANGE,
  type ResizeHandle,
  clampNumber,
  pieceIdFromInstance,
  pieceTransformToRecord,
  readArtifactTransform,
  readPieceTransform,
  resizeBoxFromHandle,
  rotateVec,
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

// Placed artifacts layer above a selected piece's transform frame (z-index 1)
// so they keep receiving pointer events; see the gizmo z-index note in CSS.
const ARTIFACT_Z_BASE = 10
// Smallest on-screen artifact box, in piece viewBox units, so a resize can't
// collapse a placement to nothing.
const ARTIFACT_MIN_DISPLAY = 6

const RESIZE_HANDLES: ResizeHandle[] = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']

export function EditorStorey({
  overview,
  pieceDescriptorBySlug,
  pieceDescriptorById,
  artifactDescriptorBySlug,
  selectedPieceId,
  selectedArtifactId,
  activeStoreyIndex,
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
  onGestureEnd,
  onRejectPlacement,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  pieceDescriptorById: Map<number, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  selectedArtifactId: number | string | null
  activeStoreyIndex: number | null
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
  /** Close the current undo-coalescing window when a drag gesture ends. */
  onGestureEnd: () => void
  /** Explain why a drop was refused, so the canvas isn't a silent red flash. */
  onRejectPlacement?: (reason: string) => void
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

  // Returns null when the drop is allowed, or a human reason when it is not.
  // Mirrors the server's ArtifactPlacement validation so the canvas refuses the
  // same drops the API would, but with an explanation instead of a 400.
  function placeRejectReason(piece: TowerLayoutPieceDescriptor, payload: PlacementDraft): string | null {
    if (!payload) return 'Nothing to place.'
    if (payload.role === 'normal') return null
    if (piece.pieceType !== 'section') return 'Interactive artifacts can only sit on a tower section.'
    const interactables = (artifactsByInstance.get(piece.instanceId) ?? []).filter(
      (artifact) => artifact.role !== 'normal',
    )
    if (payload.role === 'challenge') {
      if (interactables.some((artifact) => artifact.role !== 'challenge')) {
        return 'This section already holds a different content kind.'
      }
      if (interactables.length >= 3) return 'A section holds at most three challenges.'
      return null
    }
    if (interactables.length > 0) return 'This section already has an interactive artifact (only one is allowed).'
    return null
  }

  function canPlaceArtifact(piece: TowerLayoutPieceDescriptor, payload: PlacementDraft) {
    return placeRejectReason(piece, payload) === null
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
    const reason = placeRejectReason(piece, payload)
    if (reason !== null) {
      flashReject(pieceId)
      onRejectPlacement?.(reason)
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
    // Artifacts sit above the piece's transform frame (ARTIFACT_Z_BASE) so they
    // stay clickable while the piece is selected. The selected artifact rides one
    // step above its siblings rather than at an arbitrary 100000.
    const topSiblingZ = Math.max(0, ...placements.map((artifact) => artifact.zIndex ?? 0))
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
            zIndex: ARTIFACT_Z_BASE + (selected ? topSiblingZ + 1 : artifact.zIndex ?? 0),
          }}
          artifactDescriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
          pieceDescriptor={pieceDescriptor}
          pieceVariant={variant}
          selected={selected}
          zoomScale={zoomScale}
          onSelectArtifact={() => onSelectArtifact(artifact.id, pieceId ?? null)}
          onMoveArtifact={onMoveArtifact}
          onTransformArtifact={(next) => onTransformArtifact(artifact.id, next)}
          onGestureEnd={onGestureEnd}
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
  // The editor edits one storey at a time (storeys are tabs in InTowerEditor);
  // the canvas only mounts the active storey so authors aren't lost in a tall
  // stack. The crown caps the topmost storey only.
  const activeStorey = storeys.find((group) => group.storeyIndex === activeStoreyIndex) ?? storeys[0] ?? null
  const showCrown =
    crown !== null && (activeStorey === null || storeys[0]?.storeyIndex === activeStorey.storeyIndex)
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
        onGestureEnd={onGestureEnd}
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
            {showCrown && crown ? renderPiece(crown) : null}
            {activeStorey ? (
              <div className="editor-storey-band" key={activeStorey.storeyIndex} aria-label="Active storey">
                {activeStorey.pieces.map(renderPiece)}
              </div>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  )
}

/**
 * The on-canvas transform gizmo for the selected piece. It lives INSIDE the
 * piece element, so it inherits the piece's translate/scale/rotate and stays
 * glued to the art. The body moves the piece; the eight handles resize it
 * (corners free, edges per-axis, Shift constrains aspect) with the opposite
 * handle pinned; the top grip rotates. Edits are staged (no network) and only
 * committed when the user applies; see InTowerEditor.
 */
function PieceTransformFrame({
  transform,
  zoomScale,
  onChange,
  onGestureEnd,
}: {
  transform: PieceTransform
  zoomScale: number
  onChange: (next: PieceTransform) => void
  onGestureEnd: () => void
}) {
  function host(target: HTMLElement) {
    return (target.closest('[data-piece-id]') as HTMLElement | null) ?? target
  }

  function centreOf(target: HTMLElement) {
    const rect = host(target).getBoundingClientRect()
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
    }, onGestureEnd)
  }

  function beginResize(handle: ResizeHandle) {
    return (event: React.PointerEvent<HTMLSpanElement>) => {
      event.stopPropagation()
      event.preventDefault()
      const el = host(event.currentTarget)
      // Layout size ignores the piece's own transform and the canvas zoom, so it
      // is the un-scaled box we measure the new scale against.
      const baseW = el.offsetWidth || 1
      const baseH = el.offsetHeight || 1
      const start = transform
      const z = zoomScale || 1
      const startX = event.clientX
      const startY = event.clientY
      const w0 = baseW * start.scaleX
      const h0 = baseH * start.scaleY
      trackPointer((moveEvent) => {
        const dCanvas = { x: (moveEvent.clientX - startX) / z, y: (moveEvent.clientY - startY) / z }
        const local = rotateVec(dCanvas, -start.rotation)
        const box = resizeBoxFromHandle({
          handle,
          rotation: start.rotation,
          local,
          w0,
          h0,
          cx: start.x,
          cy: start.y,
          minW: baseW * PIECE_SCALE_RANGE.min,
          minH: baseH * PIECE_SCALE_RANGE.min,
          keepAspect: moveEvent.shiftKey,
        })
        onChange({
          ...start,
          x: Math.round(box.cx),
          y: Math.round(box.cy),
          scaleX: clampNumber(roundTo(box.w / baseW, 3), PIECE_SCALE_RANGE.min, PIECE_SCALE_RANGE.max),
          scaleY: clampNumber(roundTo(box.h / baseH, 3), PIECE_SCALE_RANGE.min, PIECE_SCALE_RANGE.max),
        })
      }, onGestureEnd)
    }
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
    }, onGestureEnd)
  }

  // Counter-scale the grips by each axis (and the canvas zoom) so they stay a
  // constant on-screen size no matter how the piece is stretched.
  const style = {
    '--ed-inv-x': 1 / Math.max(transform.scaleX * (zoomScale || 1), 0.001),
    '--ed-inv-y': 1 / Math.max(transform.scaleY * (zoomScale || 1), 0.001),
  } as CSSProperties

  return (
    <div className="ed-tf" style={style} onPointerDown={beginMove} aria-hidden="true">
      {RESIZE_HANDLES.map((handle) => (
        <span
          key={handle}
          className={`ed-tf-handle ed-tf-handle--${handle}`}
          onPointerDown={beginResize(handle)}
        />
      ))}
      <span className="ed-tf-rotate" onPointerDown={beginRotate}>
        <RotateCw className="ed-tf-rotate-icon" aria-hidden="true" />
      </span>
    </div>
  )
}

function trackPointer(move: (event: PointerEvent) => void, onEnd?: () => void) {
  const up = () => {
    window.removeEventListener('pointermove', move)
    window.removeEventListener('pointerup', up)
    onEnd?.()
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
  onGestureEnd,
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
  onGestureEnd: () => void
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
    trackPointer(move, onGestureEnd)
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
          onGestureEnd={onGestureEnd}
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
  onGestureEnd,
}: {
  artifact: ArtifactPlacementDescriptor
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  zoomScale: number
  onChange: (next: ArtifactTransform) => void
  onGestureEnd: () => void
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
    }, onGestureEnd)
  }

  // Handles drive the artifact's box (width/height) non-uniformly while its
  // uniform `scale` stays put, so dragging a corner stretches the placement.
  function beginResize(handle: ResizeHandle) {
    return (event: React.PointerEvent<HTMLSpanElement>) => {
      event.stopPropagation()
      event.preventDefault()
      const host = hostPiece(event.currentTarget)
      if (!host) return
      const start = transform
      const s = Math.max(start.scale, 0.001)
      const startPoint = clientPointToPiecePoint(event.clientX, event.clientY, host, pieceDescriptor, pieceVariant)
      const w0 = start.width * start.scale
      const h0 = start.height * start.scale
      trackPointer((moveEvent) => {
        const point = clientPointToPiecePoint(moveEvent.clientX, moveEvent.clientY, host, pieceDescriptor, pieceVariant)
        const local = rotateVec({ x: point.x - startPoint.x, y: point.y - startPoint.y }, -start.rotation)
        const box = resizeBoxFromHandle({
          handle,
          rotation: start.rotation,
          local,
          w0,
          h0,
          cx: start.x,
          cy: start.y,
          minW: ARTIFACT_MIN_DISPLAY,
          minH: ARTIFACT_MIN_DISPLAY,
          keepAspect: moveEvent.shiftKey,
        })
        onChange({
          ...start,
          x: Math.round(box.cx),
          y: Math.round(box.cy),
          width: Math.max(1, Math.round(box.w / s)),
          height: Math.max(1, Math.round(box.h / s)),
        })
      }, onGestureEnd)
    }
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
    }, onGestureEnd)
  }

  const style = { '--ed-inv': 1 / Math.max(transform.scale * (zoomScale || 1), 0.001) } as CSSProperties

  return (
    <div className="ed-tf ed-tf--artifact" style={style} onPointerDown={beginMove} aria-hidden="true">
      {RESIZE_HANDLES.map((handle) => (
        <span
          key={handle}
          className={`ed-tf-handle ed-tf-handle--${handle}`}
          onPointerDown={beginResize(handle)}
        />
      ))}
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
