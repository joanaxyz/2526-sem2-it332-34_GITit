import { Fragment, type CSSProperties, type ReactNode, useMemo, useState } from 'react'
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
import { RoofSpire, TowerBase, TowerLanding, TowerSectionShell } from '@/features/tower-map/components/TowerStoreySection'
import { TowerArtifact } from '@/features/tower-map/components/TowerArtifact'
import {
  artifactSafeBounds,
  clientPointToPiecePoint,
  pieceVariant,
  pieceViewBox,
  towerDescriptorFor,
  walkRailAnchor,
} from '@/features/tower-map/components/towerPieceData'
import type {
  TowerArtifactAssetDescriptor,
  TowerArtifactRole,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

type StoragePieceDragPayload = {
  source: 'asset-piece'
  assetId: number
  slug: string
  pieceType: TowerPieceType
  origin: 'storage'
}

type SkinPieceDragPayload = {
  source: 'asset-piece'
  assetId: number
  slug: string
  pieceType: TowerPieceType
  origin?: 'skin'
}

export type EditorDragPayload =
  | StoragePieceDragPayload
  | SkinPieceDragPayload
  // Artifacts always place as `normal`; the author promotes one to interactive
  // (and binds content) from the inspector, so the payload carries no role.
  | { source: 'asset-artifact'; assetId: number; slug: string }

export type PlacementDraft = Extract<EditorDragPayload, { source: 'asset-artifact' }> | null

type ArtifactDropResolution =
  | { status: 'ok'; pieceId: number; targetInstanceId: string; x: number; y: number }
  | { status: 'none' }

type PieceDropTarget = {
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  element: HTMLElement
}
type PiecePoint = { x: number; y: number }
type WalkRail = { x1: number; y1: number; x2: number; y2: number }
type ArtifactFootprint = Pick<ArtifactPlacementDescriptor, 'width' | 'height' | 'scale' | 'rotation'>

// Placed artifacts layer above a selected piece's transform frame (z-index 1)
// so they keep receiving pointer events; see the gizmo z-index note in CSS.
const ARTIFACT_Z_BASE = 10
// Smallest on-screen artifact box, in piece viewBox units, so a resize can't
// collapse a placement to nothing.
const ARTIFACT_MIN_DISPLAY = 6
const CENTER_SNAP_PX = 16
const LANDING_TARGET_X_PAD_PX = 10

const RESIZE_HANDLES: ResizeHandle[] = ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w']

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
  onAddPiece,
  onPlaceArtifact,
  onMoveArtifact,
  onTransformArtifact,
  onTransformPiece,
  onGestureEnd,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  pieceDescriptorById: Map<number, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  selectedArtifactId: number | string | null
  pendingSwaps: ReadonlyMap<number, number>
  pieceTransforms: ReadonlyMap<number, PieceTransform>
  artifactEdits: ReadonlyMap<number | string, ArtifactEdit>
  zoomScale: number
  placementDraft: PlacementDraft
  onSelectPiece: (pieceId: number) => void
  onSelectArtifact: (artifactId: number | string, pieceId: number | null) => void
  onSwapAsset: (pieceId: number, assetId: number) => void
  onAddPiece: (assetId: number, pieceType: TowerPieceType, sortOrder?: number) => void
  onPlaceArtifact: (pieceId: number, assetId: number, x: number, y: number) => void
  onMoveArtifact: (placementId: number | string, targetInstanceId: string, x: number, y: number) => void
  onTransformArtifact: (placementId: number | string, next: ArtifactTransform) => void
  onTransformPiece: (pieceId: number, next: PieceTransform) => void
  /** Close the current undo-coalescing window when a drag gesture ends. */
  onGestureEnd: () => void
}) {
  const layout = overview.tower_layout
  const artifactsByInstance = useMemo(() => groupArtifacts(overview.artifacts, artifactEdits), [overview.artifacts, artifactEdits])
  const [dropHoverId, setDropHoverId] = useState<number | null>(null)
  const [dropRejectHoverId, setDropRejectHoverId] = useState<number | null>(null)
  const [insertHoverIndex, setInsertHoverIndex] = useState<number | null>(null)
  const [rejectedId, setRejectedId] = useState<number | null>(null)
  const { crown, base, templatePieces } = editorTowerPieces(layout.pieces)

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
    const isActivePiece = pieceId !== null && pieceId === selectedPieceId
    const isPieceSelection = isActivePiece && selectedArtifactId === null
    const isArtifactContext = isActivePiece && selectedArtifactId !== null

    return cn(
      'editor-piece',
      isPieceSelection && 'editor-piece--selected',
      isArtifactContext && 'editor-piece--artifact-context',
      pieceId !== null && pendingSwaps.has(pieceId) && 'editor-piece--pending',
      pieceId !== null && pieceId === dropHoverId && 'editor-piece--drop',
      pieceId !== null && (pieceId === dropRejectHoverId || pieceId === rejectedId) && 'editor-piece--reject',
    )
  }

  function placePayloadAtPoint(
    payload: PlacementDraft,
    clientX: number,
    clientY: number,
    fallback?: PieceDropTarget,
  ) {
    if (!payload) return
    const footprint = artifactFootprintForPayload(payload)
    const target = pieceDropTargetAtPoint(clientX, clientY, fallback, footprint)
    if (!target) return
    // Every placed artifact starts normal, so a drop is always allowed anywhere.
    const point = artifactPointForDrop(target, clientX, clientY, footprint)
    onPlaceArtifact(target.pieceId, payload.assetId, point.x, point.y)
  }

  function artifactFootprintForPayload(payload: PlacementDraft): ArtifactFootprint {
    const descriptor = payload ? artifactDescriptorBySlug[payload.slug] ?? null : null
    const size = artifactDefaultSize(descriptor)
    return { width: size.width, height: size.height, scale: 1, rotation: 0 }
  }

  function artifactDefaultSize(descriptor: TowerArtifactAssetDescriptor | null) {
    const bounds = descriptor?.config?.bounds
    if (isArtifactBounds(bounds)) return { width: bounds.width, height: bounds.height }
    const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)
    return { width: sprite?.frame_width || 64, height: sprite?.frame_height || 64 }
  }

  function targetFromElement(element: HTMLElement): PieceDropTarget | null {
    const instanceId = element.dataset.pieceId
    if (!instanceId) return null
    const piece = layout.pieces.find((candidate) => candidate.instanceId === instanceId) ?? null
    const pieceId = piece ? pieceIdFromInstance(piece.instanceId) : null
    if (!piece || pieceId === null) return null
    return { piece, pieceId, element }
  }

  function pieceDropTargetsAtPoint(clientX: number, clientY: number): PieceDropTarget[] {
    const seen = new Set<HTMLElement>()
    const targets: PieceDropTarget[] = []
    for (const element of document.elementsFromPoint(clientX, clientY)) {
      if (!(element instanceof HTMLElement)) continue
      const pieceElement = element.closest<HTMLElement>('.editor-piece[data-piece-id]')
      if (!pieceElement || seen.has(pieceElement)) continue
      seen.add(pieceElement)
      const target = targetFromElement(pieceElement)
      if (target) targets.push(target)
    }
    return targets
  }

  function pieceDropTargetAtPoint(
    clientX: number,
    clientY: number,
    fallback?: PieceDropTarget,
    footprint?: ArtifactFootprint,
  ) {
    const railTarget = landingRailTargetAtPoint(clientX, clientY, footprint)
    if (railTarget) return railTarget

    const targets = pieceDropTargetsAtPoint(clientX, clientY)
    if (fallback && !targets.some((target) => target.element === fallback.element)) targets.push(fallback)
    if (!targets.length) return null

    const landing = bestLandingTarget(targets, clientX, clientY, footprint)
    return landing ?? targets[0]
  }

  function pieceDropTargetForInstance(targetInstanceId: string): PieceDropTarget | null {
    const piece = layout.pieces.find((candidate) => candidate.instanceId === targetInstanceId) ?? null
    const pieceId = piece ? pieceIdFromInstance(piece.instanceId) : null
    if (!piece || pieceId === null) return null
    const element =
      Array.from(document.querySelectorAll<HTMLElement>('.editor-piece[data-piece-id]')).find(
        (candidate) => candidate.dataset.pieceId === targetInstanceId,
      ) ?? null
    if (!element) return null
    return { piece, pieceId, element }
  }

  function landingRailTargetAtPoint(clientX: number, clientY: number, footprint?: ArtifactFootprint) {
    return Array.from(document.querySelectorAll<HTMLElement>('.editor-piece[data-piece-id]'))
      .map(targetFromElement)
      .filter((target): target is PieceDropTarget => target?.piece.pieceType === 'landing')
      .map((target) => ({ target, distance: landingRailDistancePx(target, clientY, footprint) }))
      .filter(({ target }) => isLandingRailCandidate(target, clientX, clientY, footprint))
      .sort((a, b) => a.distance - b.distance)[0]?.target ?? null
  }

  function bestLandingTarget(
    targets: PieceDropTarget[],
    clientX: number,
    clientY: number,
    footprint?: ArtifactFootprint,
  ) {
    return targets
      .filter((target) => target.piece.pieceType === 'landing')
      .map((target) => ({ target, distance: landingRailDistancePx(target, clientY, footprint) }))
      .filter(({ target }) => isLandingRailCandidate(target, clientX, clientY, footprint))
      .sort((a, b) => a.distance - b.distance)[0]?.target ?? null
  }

  function artifactPointForDrop(
    target: PieceDropTarget,
    clientX: number,
    clientY: number,
    footprint: ArtifactFootprint,
  ) {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const point = clientPointToPiecePoint(clientX, clientY, target.element, descriptor, variant)
    return snapArtifactPoint(target, point, footprint, { clientX, clientY })
  }

  function snapArtifactPointForInstance(
    targetInstanceId: string,
    x: number,
    y: number,
    footprint: ArtifactFootprint,
  ): PiecePoint {
    const target = pieceDropTargetForInstance(targetInstanceId)
    return target ? snapArtifactPoint(target, { x, y }, footprint) : { x: Math.round(x), y: Math.round(y) }
  }

  function snapArtifactPoint(
    target: PieceDropTarget,
    point: PiecePoint,
    footprint: ArtifactFootprint,
    pointer?: { clientX: number; clientY: number },
  ): PiecePoint {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const bounds = artifactSafeBounds(descriptor, variant) ?? pieceViewBox(descriptor, variant)
    let x = clampNumber(point.x, bounds.x, bounds.x + bounds.width)
    let y = clampNumber(point.y, bounds.y, bounds.y + bounds.height)

    if (target.piece.pieceType === 'landing') {
      const rail = numericWalkRail(descriptor, variant)
      if (rail) {
        const railMinX = Math.max(bounds.x, Math.min(rail.x1, rail.x2))
        const railMaxX = Math.min(bounds.x + bounds.width, Math.max(rail.x1, rail.x2))
        const railCenterX = railMinX <= railMaxX ? (railMinX + railMaxX) / 2 : bounds.x + bounds.width / 2
        x = railMinX <= railMaxX ? clampNumber(x, railMinX, railMaxX) : x
        y = (rail.y1 + rail.y2) / 2 - artifactVerticalRadius(footprint)
        if (shouldSnapAxis(target.element, descriptor, variant, 'x', x, railCenterX, pointer?.clientX)) {
          x = railCenterX
        }
      } else {
        y = bounds.y - artifactVerticalRadius(footprint)
        const centerX = bounds.x + bounds.width / 2
        if (shouldSnapAxis(target.element, descriptor, variant, 'x', x, centerX, pointer?.clientX)) x = centerX
      }
      return { x: Math.round(x), y: Math.round(y) }
    }

    const centerX = bounds.x + bounds.width / 2
    const centerY = bounds.y + bounds.height / 2
    if (shouldSnapAxis(target.element, descriptor, variant, 'x', x, centerX, pointer?.clientX)) x = centerX
    if (shouldSnapAxis(target.element, descriptor, variant, 'y', y, centerY, pointer?.clientY)) y = centerY
    return { x: Math.round(x), y: Math.round(y) }
  }

  function landingRailDistancePx(target: PieceDropTarget, clientY: number, footprint?: ArtifactFootprint) {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const rail = numericWalkRail(descriptor, variant)
    if (!rail) return Math.abs(clientY - target.element.getBoundingClientRect().top)
    const railY = (rail.y1 + rail.y2) / 2
    const railClientY = pieceCoordToClient(target.element, descriptor, variant, 'y', railY)
    const centerDistance = Math.abs(clientY - railClientY)
    if (!footprint) return centerDistance
    const bottomDistance = Math.abs(clientY + artifactVerticalRadiusPx(target, footprint) - railClientY)
    return Math.min(centerDistance, bottomDistance)
  }

  function isLandingRailCandidate(
    target: PieceDropTarget,
    clientX: number,
    clientY: number,
    footprint?: ArtifactFootprint,
  ) {
    // Landings are thin separators between tower sections. Treat the rail as a
    // target only when the pointer's Y is actually inside the landing element;
    // otherwise nearby sections can be stolen by the landing snap band.
    if (!pointYInsideElement(target.element, clientY)) return false
    if (pointInsideElement(target.element, clientX, clientY)) return true
    const rail = landingRailClientXRange(target)
    if (!rail) return false
    const horizontalRadius = footprint ? artifactHorizontalRadiusPx(target, footprint) : 0
    return (
      clientX >= rail.min - LANDING_TARGET_X_PAD_PX - horizontalRadius &&
      clientX <= rail.max + LANDING_TARGET_X_PAD_PX + horizontalRadius
    )
  }

  function landingRailClientXRange(target: PieceDropTarget) {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const rail = numericWalkRail(descriptor, variant)
    if (!rail) return null
    const x1 = pieceCoordToClient(target.element, descriptor, variant, 'x', rail.x1)
    const x2 = pieceCoordToClient(target.element, descriptor, variant, 'x', rail.x2)
    return { min: Math.min(x1, x2), max: Math.max(x1, x2) }
  }

  function artifactHorizontalRadiusPx(target: PieceDropTarget, footprint: ArtifactFootprint) {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const box = pieceViewBox(descriptor, variant)
    const rect = target.element.getBoundingClientRect()
    return (artifactHorizontalRadius(footprint) / Math.max(box.width, 1)) * rect.width
  }

  function artifactVerticalRadiusPx(target: PieceDropTarget, footprint: ArtifactFootprint) {
    const descriptor = descriptorFor(target.piece)
    const variant = variantForPiece(target.piece)
    const box = pieceViewBox(descriptor, variant)
    const rect = target.element.getBoundingClientRect()
    return (artifactVerticalRadius(footprint) / Math.max(box.height, 1)) * rect.height
  }

  function pointInsideElement(element: HTMLElement, clientX: number, clientY: number) {
    const rect = element.getBoundingClientRect()
    return clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom
  }

  function pointYInsideElement(element: HTMLElement, clientY: number) {
    const rect = element.getBoundingClientRect()
    return clientY >= rect.top && clientY <= rect.bottom
  }

  function shouldSnapAxis(
    element: HTMLElement,
    descriptor: TowerPieceAssetDescriptor | null,
    variant: string | undefined,
    axis: 'x' | 'y',
    value: number,
    targetValue: number,
    pointerClientValue?: number,
  ) {
    const valueClient = pointerClientValue ?? pieceCoordToClient(element, descriptor, variant, axis, value)
    const targetClient = pieceCoordToClient(element, descriptor, variant, axis, targetValue)
    return Math.abs(valueClient - targetClient) <= CENTER_SNAP_PX
  }

  function pieceCoordToClient(
    element: HTMLElement,
    descriptor: TowerPieceAssetDescriptor | null,
    variant: string | undefined,
    axis: 'x' | 'y',
    value: number,
  ) {
    const rect = element.getBoundingClientRect()
    const box = pieceViewBox(descriptor, variant)
    if (axis === 'x') return rect.left + ((value - box.x) / Math.max(box.width, 1)) * rect.width
    return rect.top + ((value - box.y) / Math.max(box.height, 1)) * rect.height
  }

  function resolveArtifactDrop(
    artifact: ArtifactFootprint,
    clientX: number,
    clientY: number,
  ): ArtifactDropResolution {
    const target = pieceDropTargetAtPoint(clientX, clientY, undefined, artifact)
    if (!target) {
      setDropHoverId(null)
      setDropRejectHoverId(null)
      return { status: 'none' }
    }

    setDropHoverId(target.pieceId)
    setDropRejectHoverId(null)

    const point = artifactPointForDrop(target, clientX, clientY, artifact)
    return {
      status: 'ok',
      pieceId: target.pieceId,
      targetInstanceId: target.piece.instanceId,
      x: point.x,
      y: point.y,
    }
  }

  function finishArtifactDrag() {
    setDropHoverId(null)
    setDropRejectHoverId(null)
    onGestureEnd()
  }

  function sortOrderForInsert(index: number): number {
    const after = templatePieces[index]
    if (typeof after?.sortOrder === 'number') return after.sortOrder
    const before = templatePieces[index - 1]
    if (typeof before?.sortOrder === 'number') return before.sortOrder + 1
    if (typeof base?.sortOrder === 'number') return base.sortOrder
    if (typeof crown?.sortOrder === 'number') return crown.sortOrder + 1
    return layout.pieces.length
  }

  function insertIndexForDrop(piece: TowerLayoutPieceDescriptor, element: HTMLElement, clientY: number): number {
    if (piece.pieceType === 'crown') return 0
    if (piece.pieceType === 'base') return templatePieces.length
    const index = templatePieces.findIndex((candidate) => candidate.instanceId === piece.instanceId)
    if (index < 0) return templatePieces.length
    const rect = element.getBoundingClientRect()
    return clientY < rect.top + rect.height / 2 ? index : index + 1
  }

  function isRepeatablePieceType(pieceType: TowerPieceType) {
    return pieceType === 'section' || pieceType === 'landing'
  }

  function isStoragePiecePayload(payload: EditorDragPayload | null): payload is StoragePieceDragPayload {
    return payload?.source === 'asset-piece' && payload.origin === 'storage'
  }

  function canInsertPiece(payload: EditorDragPayload | null): payload is StoragePieceDragPayload {
    return isStoragePiecePayload(payload) && isRepeatablePieceType(payload.pieceType)
  }

  function insertPieceFromPayload(payload: EditorDragPayload | null, index: number) {
    if (!canInsertPiece(payload)) return false
    onAddPiece(payload.assetId, payload.pieceType, sortOrderForInsert(index))
    setInsertHoverIndex(null)
    return true
  }

  function insertionHandlers(index: number) {
    return {
      onDragOver: (event: React.DragEvent<HTMLDivElement>) => {
        const meta = dragMetaFromTypes(event.dataTransfer)
        if (meta?.kind !== 'piece' || meta.origin !== 'storage' || !isRepeatablePieceType(meta.pieceType)) return
        event.preventDefault()
        event.dataTransfer.dropEffect = 'copy'
        setInsertHoverIndex(index)
        setDropHoverId(null)
        setDropRejectHoverId(null)
      },
      onDragLeave: () => {
        setInsertHoverIndex((current) => (current === index ? null : current))
      },
      onDrop: (event: React.DragEvent<HTMLDivElement>) => {
        const payload = readDrag(event)
        if (!insertPieceFromPayload(payload, index)) return
        event.preventDefault()
      },
    }
  }

  function addStoragePieceAtTarget(
    payload: EditorDragPayload | null,
    piece: TowerLayoutPieceDescriptor,
    element: HTMLElement,
    clientY: number,
  ) {
    if (!isStoragePiecePayload(payload)) return false
    if (isRepeatablePieceType(payload.pieceType)) {
      const index = insertIndexForDrop(piece, element, clientY)
      onAddPiece(payload.assetId, payload.pieceType, sortOrderForInsert(index))
    } else {
      onAddPiece(payload.assetId, payload.pieceType)
    }
    setInsertHoverIndex(null)
    return true
  }

  function regionHandlers(piece: TowerLayoutPieceDescriptor, pieceId: number | null) {
    if (pieceId === null) return {}
    return {
      role: 'button' as const,
      tabIndex: 0,
      'aria-pressed': pieceId === selectedPieceId,
      'aria-label': `${piece.pieceType} piece`,
      onClick: (event: React.MouseEvent<HTMLElement>) => {
        const target = event.target

        // Clicking an artifact or its transform gizmo should not bubble into
        // the parent piece selection, otherwise artifact selection disappears.
        if (target instanceof HTMLElement && target.closest('.editor-artifact, .ed-tf')) {
          return
        }

        if (placementDraft) {
          placePayloadAtPoint(placementDraft, event.clientX, event.clientY, {
            piece,
            pieceId,
            element: event.currentTarget,
          })
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
      onDragOver: (event: React.DragEvent<HTMLElement>) => {
        const meta = dragMetaFromTypes(event.dataTransfer)
        if (!meta) return
        event.preventDefault()
        setInsertHoverIndex(null)
        // Artifacts place as normal anywhere; pieces must match the slot type.
        if (meta.kind === 'artifact') {
          const target = pieceDropTargetAtPoint(event.clientX, event.clientY, {
            piece,
            pieceId,
            element: event.currentTarget,
          })
          event.dataTransfer.dropEffect = target ? 'copy' : 'none'
          setDropHoverId(target?.pieceId ?? null)
          setDropRejectHoverId(null)
          return
        }
        if (meta.origin === 'storage') {
          event.dataTransfer.dropEffect = 'copy'
          setDropHoverId(pieceId)
          setDropRejectHoverId(null)
          setInsertHoverIndex(
            isRepeatablePieceType(meta.pieceType)
              ? insertIndexForDrop(piece, event.currentTarget, event.clientY)
              : null,
          )
          return
        }
        // Skin swap: only lands on a piece of the same type.
        const canDrop = meta.pieceType === piece.pieceType
        event.dataTransfer.dropEffect = canDrop ? 'copy' : 'none'
        setDropHoverId(pieceId)
        setDropRejectHoverId(canDrop ? null : pieceId)
      },
      onDragLeave: () => {
        setDropHoverId((id) => (id === pieceId ? null : id))
        setDropRejectHoverId((id) => (id === pieceId ? null : id))
      },
      onDrop: (event: React.DragEvent<HTMLElement>) => {
        event.preventDefault()
        setInsertHoverIndex(null)
        setDropHoverId(null)
        setDropRejectHoverId(null)
        const payload = readDrag(event)
        if (!payload) return
        if (payload.source === 'asset-piece') {
          if (addStoragePieceAtTarget(payload, piece, event.currentTarget, event.clientY)) return
          if (payload.pieceType === piece.pieceType) onSwapAsset(pieceId, payload.assetId)
          else flashReject(pieceId)
          return
        }
        placePayloadAtPoint(payload, event.clientX, event.clientY, {
          piece,
          pieceId,
          element: event.currentTarget,
        })
      },
    }
  }

  function pieceElementForInstance(instanceId: string): HTMLElement | null {
    return (
      Array.from(document.querySelectorAll<HTMLElement>('.editor-piece[data-piece-id]')).find(
        (candidate) => candidate.dataset.pieceId === instanceId,
      ) ?? null
    )
  }

  // Where a repeatable piece dropped on open canvas (not over a piece or insert
  // line) should slot in: by the pointer's Y against each template row's midpoint.
  function templateInsertIndexAtY(clientY: number): number {
    for (let index = 0; index < templatePieces.length; index += 1) {
      const element = pieceElementForInstance(templatePieces[index].instanceId)
      if (!element) continue
      const rect = element.getBoundingClientRect()
      if (clientY < rect.top + rect.height / 2) return index
    }
    return templatePieces.length
  }

  function addPieceFromCanvasDrop(payload: EditorDragPayload | null, clientY: number): boolean {
    if (!isStoragePiecePayload(payload)) return false
    if (isRepeatablePieceType(payload.pieceType)) {
      onAddPiece(payload.assetId, payload.pieceType, sortOrderForInsert(templateInsertIndexAtY(clientY)))
    } else {
      onAddPiece(payload.assetId, payload.pieceType)
    }
    setInsertHoverIndex(null)
    return true
  }

  // Open-canvas fallback. The gaps between pieces and the gutters beside the tower
  // own no piece/insert handler, so without this a drag there reads as "no drop"
  // (the stop-sign cursor) and you could only ever drop onto an existing piece.
  // These run only when no inner handler already claimed the event
  // (defaultPrevented), so a piece swap/insert is never double-handled.
  function onCanvasDragOver(event: React.DragEvent<HTMLDivElement>) {
    if (event.defaultPrevented) return
    const meta = dragMetaFromTypes(event.dataTransfer)
    if (!meta) return
    if (meta.kind === 'artifact') {
      const target = pieceDropTargetAtPoint(event.clientX, event.clientY)
      if (!target) return
      event.preventDefault()
      event.dataTransfer.dropEffect = 'copy'
      setDropHoverId(target.pieceId)
      setDropRejectHoverId(null)
      setInsertHoverIndex(null)
      return
    }
    // Skin swaps need a piece under the pointer; on open canvas there's nothing to skin.
    if (meta.origin !== 'storage') return
    event.preventDefault()
    event.dataTransfer.dropEffect = 'copy'
    setDropHoverId(null)
    setDropRejectHoverId(null)
    setInsertHoverIndex(
      isRepeatablePieceType(meta.pieceType) ? templateInsertIndexAtY(event.clientY) : null,
    )
  }

  function onCanvasDrop(event: React.DragEvent<HTMLDivElement>) {
    if (event.defaultPrevented) return
    const payload = readDrag(event)
    if (!payload) return
    if (payload.source === 'asset-artifact') {
      event.preventDefault()
      setDropHoverId(null)
      placePayloadAtPoint(payload, event.clientX, event.clientY)
      return
    }
    if (addPieceFromCanvasDrop(payload, event.clientY)) event.preventDefault()
  }

  function onCanvasDragLeave(event: React.DragEvent<HTMLDivElement>) {
    const next = event.relatedTarget
    if (next instanceof Node && event.currentTarget.contains(next)) return
    setInsertHoverIndex(null)
    setDropHoverId(null)
    setDropRejectHoverId(null)
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
    // Artifacts sit above the piece's transform frame by default, then the
    // author's z-index value controls ordering among sibling artifacts.
    return placements.map((artifact) => {
      const edit = artifactEdits.get(artifact.id)
      const transformed = readArtifactTransform(artifact, edit)
      const selected = selectedArtifactId === artifact.id
      return (
        <EditableArtifact
          key={artifact.id}
          artifact={{
            ...artifact,
            targetInstanceId: edit?.targetInstanceId ?? artifact.targetInstanceId,
            ...transformed,
            zIndex: ARTIFACT_Z_BASE + transformed.zIndex,
          }}
          artifactDescriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
          pieceDescriptor={pieceDescriptor}
          pieceVariant={variant}
          selected={selected}
          zoomScale={zoomScale}
          onSelectArtifact={() => onSelectArtifact(artifact.id, pieceId ?? null)}
          onMoveArtifact={onMoveArtifact}
          onResolveArtifactDrop={resolveArtifactDrop}
          onSnapArtifactPoint={snapArtifactPointForInstance}
          onTransformArtifact={(next) => onTransformArtifact(artifact.id, next)}
          onArtifactDragEnd={finishArtifactDrag}
        />
      )
    })
  }

  if (layout.pieces.length === 0) {
    return (
      <div
        className="tower-stack-column tower-stack-column--editor"
        aria-label="Tower editor canvas"
        onDragOver={onCanvasDragOver}
        onDrop={onCanvasDrop}
        onDragLeave={onCanvasDragLeave}
      >
        <section className="storey-section storey-section--editor">
          <div className="learning-tower">
            <p className="editor-empty">This tower has no pieces yet.</p>
          </div>
        </section>
      </div>
    )
  }

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
    const showFrame =
      pieceId !== null &&
      pieceId === selectedPieceId &&
      selectedArtifactId === null &&
      !placementDraft
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
    if (piece.pieceType === 'base') {
      const variant = variantForPiece(piece)
      return (
        <TowerBase
          key={piece.instanceId}
          piece={renderedPiece}
          descriptor={descriptor}
          className={regionClass(pieceId)}
          {...handlers}
        >
          {frame}
          {artifactsFor(piece, descriptor, variant, pieceId)}
        </TowerBase>
      )
    }
    if (piece.pieceType === 'landing') {
      const variant = variantForPiece(piece)
      return (
        <TowerLanding
          key={piece.instanceId}
          variant={variant}
          continuation
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

  const renderInsertMarker = (index: number) => (
    <div
      key={`insert-${index}`}
      className={cn('editor-piece-insert', insertHoverIndex === index && 'is-active')}
      aria-hidden="true"
      {...insertionHandlers(index)}
    >
      <span />
    </div>
  )

  return (
    <div
      className="tower-stack-column tower-stack-column--editor"
      aria-label="Tower editor canvas"
      onDragOver={onCanvasDragOver}
      onDrop={onCanvasDrop}
      onDragLeave={onCanvasDragLeave}
    >
      <section className="storey-section storey-section--editor">
        <div className="learning-tower">
          <div className="tower-repeater">
            {crown ? renderPiece(crown) : null}
            {renderInsertMarker(0)}
            {templatePieces.map((piece, index) => (
              <Fragment key={piece.instanceId}>
                {renderPiece(piece)}
                {renderInsertMarker(index + 1)}
              </Fragment>
            ))}
            {base ? renderPiece(base) : null}
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
  onResolveArtifactDrop,
  onSnapArtifactPoint,
  onTransformArtifact,
  onArtifactDragEnd,
}: {
  artifact: ArtifactPlacementDescriptor
  artifactDescriptor: TowerArtifactAssetDescriptor | null
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  selected: boolean
  zoomScale: number
  onSelectArtifact: () => void
  onMoveArtifact: (placementId: number | string, targetInstanceId: string, x: number, y: number) => void
  onResolveArtifactDrop: (artifact: ArtifactFootprint, clientX: number, clientY: number) => ArtifactDropResolution
  onSnapArtifactPoint: (targetInstanceId: string, x: number, y: number, footprint: ArtifactFootprint) => PiecePoint
  onTransformArtifact: (next: ArtifactTransform) => void
  onArtifactDragEnd: () => void
}) {
  function onPointerDown(event: React.PointerEvent<HTMLElement>) {
    event.stopPropagation()
    event.preventDefault()
    onSelectArtifact()
    function move(ev: PointerEvent) {
      const drop = onResolveArtifactDrop(artifact, ev.clientX, ev.clientY)
      if (drop.status !== 'ok') return
      onMoveArtifact(artifact.id, drop.targetInstanceId, drop.x, drop.y)
    }
    trackPointer(move, onArtifactDragEnd)
  }

  return (
    <TowerArtifact
      artifact={artifact}
      descriptor={artifactDescriptor}
      pieceDescriptor={pieceDescriptor}
      pieceVariant={pieceVariant}
      onPointerDown={onPointerDown}
      className="editor-artifact"
    >
      {selected ? (
        <ArtifactTransformFrame
          artifact={artifact}
          pieceDescriptor={pieceDescriptor}
          pieceVariant={pieceVariant}
          zoomScale={zoomScale}
          onMoveArtifact={onMoveArtifact}
          onResolveArtifactDrop={onResolveArtifactDrop}
          onSnapArtifactPoint={onSnapArtifactPoint}
          onChange={onTransformArtifact}
          onArtifactDragEnd={onArtifactDragEnd}
          onGestureEnd={onArtifactDragEnd}
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
  onMoveArtifact,
  onResolveArtifactDrop,
  onSnapArtifactPoint,
  onChange,
  onArtifactDragEnd,
  onGestureEnd,
}: {
  artifact: ArtifactPlacementDescriptor
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  zoomScale: number
  onMoveArtifact: (placementId: number | string, targetInstanceId: string, x: number, y: number) => void
  onResolveArtifactDrop: (artifact: ArtifactFootprint, clientX: number, clientY: number) => ArtifactDropResolution
  onSnapArtifactPoint: (targetInstanceId: string, x: number, y: number, footprint: ArtifactFootprint) => PiecePoint
  onChange: (next: ArtifactTransform) => void
  onArtifactDragEnd: () => void
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
      const drop = onResolveArtifactDrop(artifact, moveEvent.clientX, moveEvent.clientY)
      if (drop.status !== 'ok') return

      if (drop.targetInstanceId !== artifact.targetInstanceId) {
        onMoveArtifact(artifact.id, drop.targetInstanceId, drop.x, drop.y)
        return
      }

      const point = clientPointToPiecePoint(moveEvent.clientX, moveEvent.clientY, host, pieceDescriptor, pieceVariant)
      const next = onSnapArtifactPoint(
        artifact.targetInstanceId,
        start.x + point.x - startPoint.x,
        start.y + point.y - startPoint.y,
        artifact,
      )
      onMoveArtifact(
        artifact.id,
        artifact.targetInstanceId,
        next.x,
        next.y,
      )
    }, onArtifactDragEnd)
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

// The browser locks `dataTransfer.getData()` during `dragover` (it only unlocks
// on `drop`), so a dragover handler can't read the JSON payload to decide whether
// to accept the drop. The *type names* stay readable throughout, though, so we
// also stamp a marker type that encodes the drag's kind. dragover handlers read
// that to allow/reject and to pick feedback; the real payload is still read from
// JSON on drop. Without this, dropping only worked where a handler happened to
// call preventDefault blindly (on top of a piece) — open canvas always rejected.
const TOWER_ARTIFACT_DRAG_TYPE = 'application/x-tower-artifact'

export type DragMeta =
  | { kind: 'artifact' }
  | { kind: 'piece'; origin: 'storage' | 'skin'; pieceType: TowerPieceType }

export function dragMarkerType(payload: EditorDragPayload): string {
  if (payload.source === 'asset-artifact') return TOWER_ARTIFACT_DRAG_TYPE
  const origin = payload.origin === 'storage' ? 'storage' : 'skin'
  return `application/x-tower-piece-${origin}-${payload.pieceType}`
}

function dragMetaFromTypes(dataTransfer: DataTransfer): DragMeta | null {
  const types = Array.from(dataTransfer.types)
  if (types.includes(TOWER_ARTIFACT_DRAG_TYPE)) return { kind: 'artifact' }
  for (const type of types) {
    const match = /^application\/x-tower-piece-(storage|skin)-([a-z]+)$/.exec(type)
    if (match) {
      return { kind: 'piece', origin: match[1] as 'storage' | 'skin', pieceType: match[2] as TowerPieceType }
    }
  }
  return null
}

function numericWalkRail(
  descriptor: TowerPieceAssetDescriptor | null,
  variant?: string,
): WalkRail | null {
  const rail = walkRailAnchor(descriptor, variant)
  if (!rail) return null
  const { x1, y1, x2, y2 } = rail
  if (x1 === null || y1 === null || x2 === null || y2 === null) return null
  return { x1, y1, x2, y2 }
}

function artifactHorizontalRadius(footprint: ArtifactFootprint) {
  const width = Math.max(0, footprint.width * footprint.scale)
  const height = Math.max(0, footprint.height * footprint.scale)
  const radians = (footprint.rotation * Math.PI) / 180
  return (Math.abs(Math.cos(radians)) * width + Math.abs(Math.sin(radians)) * height) / 2
}

function artifactVerticalRadius(footprint: ArtifactFootprint) {
  const width = Math.max(0, footprint.width * footprint.scale)
  const height = Math.max(0, footprint.height * footprint.scale)
  const radians = (footprint.rotation * Math.PI) / 180
  return (Math.abs(Math.sin(radians)) * width + Math.abs(Math.cos(radians)) * height) / 2
}

function isArtifactBounds(value: unknown): value is { width: number; height: number } {
  if (typeof value !== 'object' || value === null) return false
  const maybe = value as { width?: unknown; height?: unknown }
  return Number.isFinite(Number(maybe.width)) && Number.isFinite(Number(maybe.height))
}

function firstInteractableRole(artifacts: ArtifactPlacementDescriptor[]): TowerArtifactRole {
  return artifacts.find((artifact) => artifact.role !== 'normal')?.role ?? 'normal'
}

function groupArtifacts(
  artifacts: ArtifactPlacementDescriptor[],
  artifactEdits?: ReadonlyMap<number | string, ArtifactEdit>,
) {
  const map = new Map<string, ArtifactPlacementDescriptor[]>()
  for (const artifact of artifacts) {
    const targetInstanceId = artifactEdits?.get(artifact.id)?.targetInstanceId ?? artifact.targetInstanceId
    const placed = targetInstanceId === artifact.targetInstanceId ? artifact : { ...artifact, targetInstanceId }
    const list = map.get(targetInstanceId) ?? []
    list.push(placed)
    map.set(targetInstanceId, list)
  }
  return map
}

function editorTowerPieces(pieces: TowerLayoutPieceDescriptor[]) {
  const crown = pieces.find((piece) => piece.pieceType === 'crown') ?? null
  const base = pieces.find((piece) => piece.pieceType === 'base') ?? null
  const templatePieces = pieces.filter((piece) => piece.pieceType !== 'crown' && piece.pieceType !== 'base')
  return {
    crown,
    base,
    templatePieces,
  }
}
