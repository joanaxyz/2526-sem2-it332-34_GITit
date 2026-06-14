import { useRef, useState } from 'react'
import { Trash2, X } from 'lucide-react'

import { pieceArt } from '@/features/tower-designs/components/EditorCanvas'
import type { PaletteDragPayload } from '@/features/tower-designs/components/PiecePalette'
import { PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { towerPieceAttrs } from '@/features/tower-map/components/towerPieceData'
import { backendUrl } from '@/shared/api/httpClient'
import type {
  TowerArtifactAssetDescriptor,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
} from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

function readDrag(event: React.DragEvent): PaletteDragPayload | null {
  try {
    return JSON.parse(event.dataTransfer.getData('application/json')) as PaletteDragPayload
  } catch {
    return null
  }
}

function thumb(descriptor: TowerArtifactAssetDescriptor): string | null {
  const sprite = descriptor.sprites.default ?? Object.values(descriptor.sprites)[0]
  return sprite?.url ? backendUrl(sprite.url) : null
}

/**
 * Focused editor for a single tower section: a large zoomed view of the piece
 * with its artifacts, plus an artifact palette to drag new pieces onto it.
 * Stays inside the tower page (rendered as an overlay), so exiting drops the
 * author straight back onto the editor canvas. The same surface authors a
 * battle landing's backdrop (the `landing` piece) — artifacts dropped here are
 * the customizable stage dressing.
 */
export function SectionEditor({
  overview,
  piece,
  descriptor,
  artifactDescriptors,
  artifactDescriptorBySlug,
  onPlaceArtifact,
  onMoveArtifact,
  onDeleteArtifact,
  onClose,
}: {
  overview: TowerDesignOverview
  piece: TowerLayoutPieceDescriptor
  descriptor: TowerPieceAssetDescriptor | null
  artifactDescriptors: TowerArtifactAssetDescriptor[]
  artifactDescriptorBySlug: Record<string, TowerArtifactAssetDescriptor>
  onPlaceArtifact: (pieceId: number, assetId: number, x: number, y: number) => void
  onMoveArtifact: (placementId: number, x: number, y: number) => void
  onDeleteArtifact: (placementId: number) => void
  onClose: () => void
}) {
  const stageRef = useRef<HTMLDivElement | null>(null)
  const [dropHover, setDropHover] = useState(false)
  const [selectedArtifact, setSelectedArtifact] = useState<number | null>(null)

  const pieceId = piece ? Number(/-piece-(\d+)$/.exec(piece.instanceId)?.[1]) : null
  const artifacts = overview.artifacts.filter((a) => a.targetInstanceId === piece.instanceId)
  const isLanding = piece.pieceType === 'landing'

  function onDrop(event: React.DragEvent) {
    event.preventDefault()
    setDropHover(false)
    const payload = readDrag(event)
    if (!payload || payload.source !== 'palette-artifact' || pieceId === null) return
    const rect = stageRef.current?.getBoundingClientRect()
    const x = rect ? event.clientX - rect.left : 0
    const y = rect ? event.clientY - rect.top : 0
    onPlaceArtifact(pieceId, payload.assetId, Math.round(x), Math.round(y))
  }

  return (
    <div className="section-editor-overlay" role="dialog" aria-label="Section editor" aria-modal="true">
      <header className="section-editor-bar">
        <div>
          <p className="editor-eyebrow">Section editor</p>
          <h2 className="editor-title">{PIECE_TYPE_LABEL[piece.pieceType] ?? piece.pieceType}</h2>
        </div>
        <p className="section-editor-hint">
          {isLanding
            ? 'Drag artifacts onto the landing to dress the battle stage. Drag placed pieces to move them.'
            : 'Drag artifacts onto the section. Drag placed pieces to move them.'}
        </p>
        <button type="button" className="editor-icon-btn" onClick={onClose} aria-label="Close section editor">
          <X className="size-4" aria-hidden="true" />
        </button>
      </header>

      <div className="section-editor-body">
        <div
          ref={stageRef}
          className={cn('section-editor-stage', `editor-slot--${piece.pieceType}`, dropHover && 'is-drop-target')}
          {...towerPieceAttrs(piece, descriptor)}
          onDrop={onDrop}
          onDragOver={(event) => {
            event.preventDefault()
            event.dataTransfer.dropEffect = 'copy'
            setDropHover(true)
          }}
          onDragLeave={() => setDropHover(false)}
          onClick={() => setSelectedArtifact(null)}
        >
          <span className="editor-slot-art" aria-hidden="true">
            {pieceArt(piece.pieceType, descriptor, false)}
          </span>

          {artifacts.map((artifact) => (
            <PlacedArtifact
              key={artifact.id}
              artifact={artifact}
              descriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
              stageRef={stageRef}
              selected={selectedArtifact === artifact.id}
              onSelect={() => setSelectedArtifact(artifact.id)}
              onMove={onMoveArtifact}
            />
          ))}
        </div>

        <aside className="section-editor-rail" aria-label="Artifacts">
          <h3 className="editor-rail-title">Artifacts</h3>
          <p className="editor-palette-active">Drag onto the section.</p>
          <div className="section-editor-artifact-grid">
            {artifactDescriptors.map((art) => {
              const url = thumb(art)
              return (
                <button
                  type="button"
                  key={art.slug}
                  className="editor-palette-cell"
                  draggable
                  title={art.label}
                  aria-label={art.label}
                  onDragStart={(event) => {
                    const payload: PaletteDragPayload = {
                      source: 'palette-artifact',
                      assetId: art.id,
                      slug: art.slug,
                    }
                    event.dataTransfer.setData('application/json', JSON.stringify(payload))
                    event.dataTransfer.effectAllowed = 'copy'
                  }}
                >
                  <span className="editor-palette-thumb">{url ? <img src={url} alt="" draggable={false} /> : null}</span>
                </button>
              )
            })}
            {artifactDescriptors.length === 0 ? (
              <p className="editor-palette-empty">No artifacts yet — upload or buy some.</p>
            ) : null}
          </div>

          {selectedArtifact !== null ? (
            <div className="section-editor-selected">
              <button
                type="button"
                className="editor-danger-btn"
                onClick={() => {
                  onDeleteArtifact(selectedArtifact)
                  setSelectedArtifact(null)
                }}
              >
                <Trash2 className="size-4" aria-hidden="true" />
                Remove artifact
              </button>
            </div>
          ) : null}
        </aside>
      </div>
    </div>
  )
}

function PlacedArtifact({
  artifact,
  descriptor,
  stageRef,
  selected,
  onSelect,
  onMove,
}: {
  artifact: ArtifactPlacementDescriptor
  descriptor: TowerArtifactAssetDescriptor | null
  stageRef: React.RefObject<HTMLDivElement | null>
  selected: boolean
  onSelect: () => void
  onMove: (placementId: number, x: number, y: number) => void
}) {
  const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)

  function onPointerDown(event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    onSelect()
    const rect = stageRef.current?.getBoundingClientRect()
    if (!rect) return
    const { left, top } = rect
    function move(ev: PointerEvent) {
      onMove(artifact.id, Math.round(ev.clientX - left), Math.round(ev.clientY - top))
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
      className={cn('editor-artifact', selected && 'is-selected')}
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
