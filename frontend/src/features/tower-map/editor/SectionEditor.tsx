import { useRef, useState } from 'react'
import { Trash2, X } from 'lucide-react'

import type { PaletteDragPayload } from '@/features/tower-designs/components/PiecePalette'
import { PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { PieceArt } from '@/features/tower-map/components/PieceArt'
import {
  artifactSafeBounds,
  clientPointToPiecePoint,
  piecePointToCss,
  pieceVariant,
  pieceViewBox,
  towerPieceAttrs,
} from '@/features/tower-map/components/towerPieceData'
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
  onUpdateArtifact,
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
  onUpdateArtifact: (placementId: number, patch: { scale?: number; rotation?: number }) => void
  onDeleteArtifact: (placementId: number) => void
  onClose: () => void
}) {
  const stageRef = useRef<HTMLDivElement | null>(null)
  const [dropHover, setDropHover] = useState(false)
  const [selectedArtifact, setSelectedArtifact] = useState<number | null>(null)
  // Live draft of the selected artifact's transform: the sliders move it
  // instantly; we persist on release so we don't PATCH on every tick.
  const [draft, setDraft] = useState<{ scale: number; rotation: number } | null>(null)

  const pieceId = piece ? Number(/-piece-(\d+)$/.exec(piece.instanceId)?.[1]) : null
  const artifacts = overview.artifacts.filter((a) => a.targetInstanceId === piece.instanceId)
  const selected = selectedArtifact === null ? null : artifacts.find((a) => a.id === selectedArtifact) ?? null
  const variant = pieceVariant(overview.tower_layout, piece)
  const isLanding = piece.pieceType === 'landing'

  function selectArtifact(artifact: ArtifactPlacementDescriptor) {
    setSelectedArtifact(artifact.id)
    setDraft({ scale: artifact.scale, rotation: artifact.rotation })
  }

  function placeAtCenter(assetId: number) {
    if (pieceId === null) return
    const safe = artifactSafeBounds(descriptor, variant)
    const box = pieceViewBox(descriptor, variant)
    onPlaceArtifact(
      pieceId,
      assetId,
      Math.round(safe ? safe.x + safe.width / 2 : box.x + box.width / 2),
      Math.round(safe ? safe.y + safe.height / 2 : box.y + box.height / 2),
    )
  }

  function onDrop(event: React.DragEvent) {
    event.preventDefault()
    setDropHover(false)
    const payload = readDrag(event)
    if (!payload || payload.source !== 'palette-artifact' || pieceId === null) return
    const rect = stageRef.current?.getBoundingClientRect()
    if (!rect || !stageRef.current) return
    const point = clientPointToPiecePoint(event.clientX, event.clientY, stageRef.current, descriptor, variant)
    onPlaceArtifact(pieceId, payload.assetId, Math.round(point.x), Math.round(point.y))
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
          {...towerPieceAttrs(piece, descriptor, { variant })}
          onDrop={onDrop}
          onDragOver={(event) => {
            event.preventDefault()
            event.dataTransfer.dropEffect = 'copy'
            setDropHover(true)
          }}
          onDragLeave={() => setDropHover(false)}
          onClick={() => {
            setSelectedArtifact(null)
            setDraft(null)
          }}
        >
          <span className="editor-slot-art" aria-hidden="true">
            <PieceArt pieceType={piece.pieceType} descriptor={descriptor} variant={variant} />
          </span>

          {artifacts.map((artifact) => {
            const isSel = selectedArtifact === artifact.id
            return (
              <PlacedArtifact
                key={artifact.id}
                artifact={artifact}
                descriptor={artifactDescriptorBySlug[artifact.assetSlug] ?? null}
                pieceDescriptor={descriptor}
                pieceVariant={variant}
                stageRef={stageRef}
                selected={isSel}
                scale={isSel && draft ? draft.scale : artifact.scale}
                rotation={isSel && draft ? draft.rotation : artifact.rotation}
                onSelect={() => selectArtifact(artifact)}
                onMove={onMoveArtifact}
              />
            )
          })}
        </div>

        <aside className="section-editor-rail" aria-label="Artifacts">
          <h3 className="editor-rail-title">Artifacts</h3>
          <p className="editor-palette-active">Click to drop one on the section, or drag to place it exactly.</p>
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
                  aria-label={`Place ${art.label}`}
                  onClick={() => placeAtCenter(art.id)}
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

          {selected && draft ? (
            <div className="section-editor-selected">
              <h4 className="editor-panel-title">Selected artifact</h4>
              <label className="editor-control">
                <span className="editor-control-label">
                  Size <span className="editor-control-value">{Math.round(draft.scale * 100)}%</span>
                </span>
                <input
                  type="range"
                  min="0.3"
                  max="2.5"
                  step="0.05"
                  value={draft.scale}
                  onChange={(e) => setDraft({ ...draft, scale: Number(e.target.value) })}
                  onPointerUp={() => onUpdateArtifact(selected.id, { scale: draft.scale })}
                  onKeyUp={() => onUpdateArtifact(selected.id, { scale: draft.scale })}
                />
              </label>
              <label className="editor-control">
                <span className="editor-control-label">
                  Rotation <span className="editor-control-value">{Math.round(draft.rotation)}°</span>
                </span>
                <input
                  type="range"
                  min="-180"
                  max="180"
                  step="1"
                  value={draft.rotation}
                  onChange={(e) => setDraft({ ...draft, rotation: Number(e.target.value) })}
                  onPointerUp={() => onUpdateArtifact(selected.id, { rotation: draft.rotation })}
                  onKeyUp={() => onUpdateArtifact(selected.id, { rotation: draft.rotation })}
                />
              </label>
              <button
                type="button"
                className="editor-danger-btn"
                onClick={() => {
                  onDeleteArtifact(selected.id)
                  setSelectedArtifact(null)
                  setDraft(null)
                }}
              >
                <Trash2 className="size-4" aria-hidden="true" />
                Remove artifact
              </button>
            </div>
          ) : (
            <p className="editor-palette-active">Select a placed artifact to resize or rotate it.</p>
          )}
        </aside>
      </div>
    </div>
  )
}

function PlacedArtifact({
  artifact,
  descriptor,
  pieceDescriptor,
  pieceVariant,
  stageRef,
  selected,
  scale,
  rotation,
  onSelect,
  onMove,
}: {
  artifact: ArtifactPlacementDescriptor
  descriptor: TowerArtifactAssetDescriptor | null
  pieceDescriptor: TowerPieceAssetDescriptor | null
  pieceVariant?: string
  stageRef: React.RefObject<HTMLDivElement | null>
  selected: boolean
  /** Live transform (the sliders preview before persisting). */
  scale: number
  rotation: number
  onSelect: () => void
  onMove: (placementId: number, x: number, y: number) => void
}) {
  const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)

  function onPointerDown(event: React.PointerEvent) {
    event.stopPropagation()
    event.preventDefault()
    onSelect()
    const stage = stageRef.current
    if (!stage) return
    const stageEl: HTMLElement = stage
    function move(ev: PointerEvent) {
      const point = clientPointToPiecePoint(ev.clientX, ev.clientY, stageEl, pieceDescriptor, pieceVariant)
      onMove(artifact.id, Math.round(point.x), Math.round(point.y))
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
        ...piecePointToCss(artifact.x, artifact.y, pieceDescriptor, pieceVariant),
        transform: `translate(-50%, -50%) scale(${scale}) rotate(${rotation}deg)`,
        zIndex: artifact.zIndex,
      }}
      onPointerDown={onPointerDown}
    >
      {sprite?.url ? <img src={backendUrl(sprite.url)} alt="" draggable={false} /> : null}
    </span>
  )
}
