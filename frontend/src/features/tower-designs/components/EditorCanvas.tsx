import { useRef, useState } from 'react'

import type { PaletteDragPayload } from '@/features/tower-designs/components/PiecePalette'
import { PIECE_TYPE_LABEL, pieceIdFromInstance } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import {
  AdventureSectionPiece,
  ChallengeSectionPiece,
  DoorPiece,
  LandingPiece,
  SpirePiece,
  TomePiece,
} from '@/features/tower-map/components/TowerPieces'
import { towerDescriptorFor, towerPieceAttrs } from '@/features/tower-map/components/towerPieceData'
import type {
  TowerArtifactAssetDescriptor,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { backendUrl } from '@/shared/api/httpClient'
import { cn } from '@/shared/utils/cn'

function readDrag(event: React.DragEvent): PaletteDragPayload | null {
  try {
    return JSON.parse(event.dataTransfer.getData('application/json')) as PaletteDragPayload
  } catch {
    return null
  }
}

export function pieceArt(pieceType: string, descriptor: TowerPieceAssetDescriptor | null, isFirst: boolean) {
  switch (pieceType) {
    case 'spire':
      return (
        <>
          <SpirePiece descriptor={descriptor} />
          {isFirst ? (
            <div className="tower-window-roof">
              <span className="tower-window-roof-spire" />
              <span className="tower-window-roof-peak" />
            </div>
          ) : null}
        </>
      )
    case 'landing':
      return <LandingPiece descriptor={descriptor} />
    case 'adventure_section':
      return <AdventureSectionPiece descriptor={descriptor} />
    case 'challenge_section':
      return <ChallengeSectionPiece descriptor={descriptor} />
    case 'tome':
      return <TomePiece descriptor={descriptor} />
    case 'door':
      return <DoorPiece descriptor={descriptor} />
    default:
      return null
  }
}

export function EditorCanvas({
  overview,
  pieceDescriptorBySlug,
  artifactDescriptorBySlug,
  selectedPieceId,
  onSelectPiece,
  onSwapAsset,
  onPlaceArtifact,
  onMoveArtifact,
  onOpenSection,
}: {
  overview: TowerDesignOverview
  pieceDescriptorBySlug: Record<string, TowerPieceAssetDescriptor>
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  selectedPieceId: number | null
  onSelectPiece: (pieceId: number) => void
  onSwapAsset: (pieceId: number, assetId: number) => void
  onPlaceArtifact: (pieceId: number, assetId: number, x: number, y: number) => void
  onMoveArtifact: (placementId: number, x: number, y: number) => void
  /** Double-click / Enter+shift on a slot opens the focused section editor. */
  onOpenSection?: (pieceId: number) => void
}) {
  const pieces = overview.tower_layout.pieces
  const artifactsByInstance = groupArtifacts(overview.artifacts)
  // Group pieces into storey bands so the author sees which storey each piece
  // (and its bound content) belongs to. Pieces keep their global order.
  const storeyOrder: number[] = []
  for (const piece of pieces) {
    const idx = piece.storeyIndex ?? 0
    if (!storeyOrder.includes(idx)) storeyOrder.push(idx)
  }
  const multiStorey = storeyOrder.length > 1
  let globalIndex = 0

  return (
    <div className="editor-stage" aria-label="Tower editor canvas">
      <p className="editor-stage-kicker">A storey repeats up the tower — design it once.</p>
      <div className="tower-editor-stage">
        <div className="learning-tower">
          <div className="tower-repeater">
            {storeyOrder.map((storeyIndex) => {
              const storeyPieces = pieces.filter((p) => (p.storeyIndex ?? 0) === storeyIndex)
              return (
                <div className="editor-storey-band" key={`storey-${storeyIndex}`}>
                  {multiStorey ? <span className="editor-storey-label">Storey {storeyIndex + 1}</span> : null}
                  {storeyPieces.map((piece) => {
                    const isFirst = globalIndex === 0
                    globalIndex += 1
                    return (
                      <EditorSlot
                        key={piece.instanceId}
                        piece={piece}
                        descriptor={towerDescriptorFor(piece, pieceDescriptorBySlug)}
                        artifactDescriptorBySlug={artifactDescriptorBySlug}
                        artifacts={artifactsByInstance.get(piece.instanceId) ?? []}
                        isFirst={isFirst}
                        selected={pieceIdFromInstance(piece.instanceId) === selectedPieceId}
                        onSelectPiece={onSelectPiece}
                        onSwapAsset={onSwapAsset}
                        onPlaceArtifact={onPlaceArtifact}
                        onMoveArtifact={onMoveArtifact}
                        onOpenSection={onOpenSection}
                      />
                    )
                  })}
                </div>
              )
            })}
            {pieces.length === 0 ? (
              <p className="editor-empty">This tower has no pieces yet.</p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  )
}

function EditorSlot({
  piece,
  descriptor,
  artifacts,
  artifactDescriptorBySlug,
  isFirst,
  selected,
  onSelectPiece,
  onSwapAsset,
  onPlaceArtifact,
  onMoveArtifact,
  onOpenSection,
}: {
  piece: TowerLayoutPieceDescriptor
  descriptor: TowerPieceAssetDescriptor | null
  artifacts: ArtifactPlacementDescriptor[]
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  isFirst: boolean
  selected: boolean
  onSelectPiece: (pieceId: number) => void
  onSwapAsset: (pieceId: number, assetId: number) => void
  onPlaceArtifact: (pieceId: number, assetId: number, x: number, y: number) => void
  onMoveArtifact: (placementId: number, x: number, y: number) => void
  onOpenSection?: (pieceId: number) => void
}) {
  const pieceId = pieceIdFromInstance(piece.instanceId)
  const slotRef = useRef<HTMLDivElement | null>(null)
  const [dropHover, setDropHover] = useState<'piece' | 'artifact' | null>(null)
  const [rejected, setRejected] = useState(false)

  function flashReject() {
    setRejected(true)
    window.setTimeout(() => setRejected(false), 1100)
  }

  function onDrop(event: React.DragEvent) {
    event.preventDefault()
    setDropHover(null)
    const payload = readDrag(event)
    if (!payload || pieceId === null) return
    if (payload.source === 'palette-piece') {
      if (payload.pieceType === piece.pieceType) onSwapAsset(pieceId, payload.assetId)
      else flashReject()
      return
    }
    if (payload.source === 'palette-artifact') {
      const rect = slotRef.current?.getBoundingClientRect()
      const x = rect ? event.clientX - rect.left : 0
      const y = rect ? event.clientY - rect.top : 0
      onPlaceArtifact(pieceId, payload.assetId, Math.round(x), Math.round(y))
    }
  }

  function onDragOver(event: React.DragEvent) {
    event.preventDefault()
    // Without an explicit dropEffect some browsers refuse to fire `drop`.
    event.dataTransfer.dropEffect = 'copy'
    const payload = readDrag(event)
    // dataTransfer.getData is empty during dragover in some browsers; fall back to hover hint.
    const next = payload?.source === 'palette-artifact' ? 'artifact' : 'piece'
    setDropHover(next)
  }

  return (
    <div
      ref={slotRef}
      className={cn(
        'editor-slot',
        `editor-slot--${piece.pieceType}`,
        selected && 'is-selected',
        dropHover && 'is-drop-target',
        rejected && 'is-drop-reject',
      )}
      role="button"
      tabIndex={0}
      aria-pressed={selected}
      aria-label={`${piece.pieceType} slot`}
      {...towerPieceAttrs(piece, descriptor)}
      onClick={() => pieceId !== null && onSelectPiece(pieceId)}
      onDoubleClick={() => pieceId !== null && onOpenSection?.(pieceId)}
      onKeyDown={(event) => {
        if ((event.key === 'Enter' || event.key === ' ') && pieceId !== null) {
          event.preventDefault()
          if (event.shiftKey) onOpenSection?.(pieceId)
          else onSelectPiece(pieceId)
        }
      }}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={() => setDropHover(null)}
    >
      <span className="editor-slot-art" aria-hidden="true">
        {pieceArt(piece.pieceType, descriptor, isFirst)}
      </span>

      {piece.contentBinding ? <span className="editor-slot-badge">bound</span> : null}

      {rejected ? (
        <span className="editor-slot-reject" role="status">
          Drop a {PIECE_TYPE_LABEL[piece.pieceType] ?? piece.pieceType} here
        </span>
      ) : null}

      {artifacts.map((artifact) => (
        <ArtifactOverlay
          key={artifact.id}
          artifact={artifact}
          descriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
          slotRef={slotRef}
          onMoveArtifact={onMoveArtifact}
        />
      ))}
    </div>
  )
}

function ArtifactOverlay({
  artifact,
  descriptor,
  slotRef,
  onMoveArtifact,
}: {
  artifact: ArtifactPlacementDescriptor
  descriptor: TowerArtifactAssetDescriptor | null
  slotRef: React.RefObject<HTMLDivElement | null>
  onMoveArtifact: (placementId: number, x: number, y: number) => void
}) {
  const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)

  function onPointerDown(event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    const rect = slotRef.current?.getBoundingClientRect()
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

function groupArtifacts(artifacts: ArtifactPlacementDescriptor[]) {
  const map = new Map<string, ArtifactPlacementDescriptor[]>()
  for (const artifact of artifacts) {
    const list = map.get(artifact.targetInstanceId) ?? []
    list.push(artifact)
    map.set(artifact.targetInstanceId, list)
  }
  return map
}
