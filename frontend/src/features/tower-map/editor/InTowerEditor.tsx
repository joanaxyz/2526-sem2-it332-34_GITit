import { useEffect, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Check, Copy, Layers, Maximize2, Share2, UploadCloud } from 'lucide-react'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import type { ContentKind } from '@/features/authoring/types'
import {
  ARTIFACT_ROLE_LABEL,
  INTERACTABLE_ROLES,
  PIECE_TYPE_LABEL,
  pieceIdFromInstance,
} from '@/features/tower-designs/editorUtils'
import {
  EditorStorey,
  type EditorDragPayload,
  type PlacementDraft,
} from '@/features/tower-designs/components/EditorStorey'
import { UploadAssetDialog } from '@/features/tower-designs/components/UploadAssetDialog'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { useDesignEditor } from '@/features/tower-designs/hooks/useDesignEditor'
import { pieceHasWalkRail } from '@/features/tower-map/components/towerPieceData'
import { useZoomPan, type ZoomPan } from '@/features/tower-map/editor/useZoomPan'
import { backendUrl } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import type { TowerArtifactRole, TowerLayoutPieceDescriptor, TowerPieceAssetDescriptor, TowerPieceType } from '@/shared/assets/types'
import { ApiError } from '@/shared/api/apiError'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

function TowerNameField({
  title,
  pending,
  onRename,
}: {
  title: string
  pending: boolean
  onRename: (next: string) => void
}) {
  const [draft, setDraft] = useState(title)

  function commit() {
    const next = draft.trim()
    if (next && next !== title) onRename(next)
    else setDraft(title)
  }

  return (
    <input
      className="ite-name-input"
      value={draft}
      disabled={pending}
      aria-label="Tower name"
      onChange={(e) => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => {
        if (e.key === 'Enter') e.currentTarget.blur()
        if (e.key === 'Escape') {
          setDraft(title)
          e.currentTarget.blur()
        }
      }}
    />
  )
}

function publishErrorMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) return error ? 'Could not publish.' : null
  const payload = error.payload as { detail?: string; validation_errors?: { message: string }[] } | null
  if (payload?.validation_errors?.length) {
    return payload.validation_errors.map((row) => row.message).join(' ')
  }
  return payload?.detail ?? error.message
}

export function InTowerEditor({
  designId,
  storeyId = null,
}: {
  designId: number
  storeyId?: number | null
}) {
  const editor = useDesignEditor(designId)
  const zoom = useZoomPan()
  const [selectedPieceId, setSelectedPieceId] = useState<number | null>(null)
  const [selectedStoreyIndex, setSelectedStoreyIndex] = useState<number | null>(storeyId)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [placementDraft, setPlacementDraft] = useState<PlacementDraft>(null)
  const [pendingSwaps, setPendingSwaps] = useState<Map<number, number>>(new Map())
  const [applying, setApplying] = useState(false)

  const pieceDescriptorById = useMemo(
    () => new Map(editor.pieceDescriptors.map((d) => [d.id, d])),
    [editor.pieceDescriptors],
  )

  const shared = editor.share.data
  const shareUrl = shared?.share_path ? `${window.location.origin}${shared.share_path}` : null
  const shareError = publishErrorMessage(editor.share.error)

  const walkRailWarnings = useMemo(() => {
    if (!editor.overview) return []
    return editor.overview.tower_layout.pieces
      .filter((p) => p.pieceType === 'landing')
      .filter((p) => !pieceHasWalkRail(editor.pieceDescriptorBySlug[p.assetSlug]))
  }, [editor.overview, editor.pieceDescriptorBySlug])
  const storeyIndexes = useMemo(() => uniqueStoreyIndexes(editor.overview), [editor.overview])
  const activeStoreyIndex = useMemo(
    () => resolveActiveStoreyIndex(storeyIndexes, selectedStoreyIndex, storeyId),
    [storeyIndexes, selectedStoreyIndex, storeyId],
  )

  useEffect(() => {
    if (typeof storeyId === 'number') setSelectedStoreyIndex(storeyId)
  }, [storeyId])

  useEffect(() => {
    if (selectedPieceId === null || activeStoreyIndex === null || !editor.overview) return
    const selectedPiece = editor.overview.tower_layout.pieces.find(
      (piece) => pieceIdFromInstance(piece.instanceId) === selectedPieceId,
    )
    if (
      selectedPiece &&
      selectedPiece.pieceType !== 'crown' &&
      normalizedStoreyIndex(selectedPiece) !== activeStoreyIndex
    ) {
      setSelectedPieceId(null)
      setPlacementDraft(null)
    }
  }, [activeStoreyIndex, editor.overview, selectedPieceId])

  if (editor.isLoading) return <LoadingState label="Opening the editor" variant="page" />
  if (editor.isError || !editor.overview) {
    return <ErrorState title="Could not open this tower" description={(editor.error as Error)?.message ?? ''} />
  }

  const overview = editor.overview
  const isFork = overview.design.origin === 'official_fork'
  const publishError = publishErrorMessage(editor.publish.error)

  function copyShareUrl() {
    if (!shareUrl) return
    void navigator.clipboard?.writeText(shareUrl).then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    })
  }

  function pickSwap(pieceId: number, assetId: number) {
    const piece = overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === pieceId)
    const committedId = piece ? editor.pieceDescriptorBySlug[piece.assetSlug]?.id ?? null : null
    setPendingSwaps((prev) => {
      const next = new Map(prev)
      if (assetId === committedId) next.delete(pieceId)
      else next.set(pieceId, assetId)
      return next
    })
  }

  async function applyPending() {
    setApplying(true)
    try {
      await Promise.all(
        [...pendingSwaps.entries()].map(([pieceId, assetId]) => editor.swapAsset.mutateAsync({ pieceId, assetId })),
      )
      setPendingSwaps(new Map())
    } finally {
      setApplying(false)
    }
  }

  function addStorey() {
    editor.addStorey.mutate(undefined, {
      onSuccess: (payload) => {
        setSelectedStoreyIndex(payload.added_storey_index)
        setSelectedPieceId(null)
        setPlacementDraft(null)
      },
    })
  }

  function artifactSize(assetId: number) {
    const descriptor = editor.artifactDescriptors.find((artifact) => artifact.id === assetId)
    const bounds = descriptor?.config?.bounds
    if (isBounds(bounds)) return { width: bounds.width, height: bounds.height }
    const sprite = descriptor?.sprites.default ?? (descriptor ? Object.values(descriptor.sprites)[0] : null)
    return { width: sprite?.frame_width || 64, height: sprite?.frame_height || 64 }
  }

  const previewAssetId = selectedPieceId !== null ? pendingSwaps.get(selectedPieceId) ?? null : null

  return (
    <div className="in-tower-editor">
      {uploadOpen ? <UploadAssetDialog onClose={() => setUploadOpen(false)} /> : null}

      <section
        className="tower-stage-grid tower-stage-grid--editor"
        aria-label="Tower editor canvas"
        onWheel={zoom.onWheel}
        onPointerDown={zoom.onPanStart}
        style={zoom.style}
      >
        <EditorStorey
          overview={overview}
          pieceDescriptorBySlug={editor.pieceDescriptorBySlug}
          pieceDescriptorById={pieceDescriptorById}
          artifactDescriptorBySlug={editor.artifactDescriptorBySlug}
          selectedPieceId={selectedPieceId}
          pendingSwaps={pendingSwaps}
          placementDraft={placementDraft}
          storeyIndex={activeStoreyIndex}
          onSelectPiece={(pieceId) => {
            setSelectedPieceId(pieceId)
            setPlacementDraft(null)
          }}
          onSwapAsset={pickSwap}
          onPlaceArtifact={(pieceId, assetId, role, contentDefinitionId, x, y) => {
            const size = artifactSize(assetId)
            editor.placeArtifact.mutate({
              target_piece_instance_id: pieceId,
              artifact_asset_id: assetId,
              role,
              content_definition_id: contentDefinitionId ?? null,
              x,
              y,
              width: size.width,
              height: size.height,
            })
            setPlacementDraft(null)
          }}
          onMoveArtifact={(placementId, x, y) => editor.updateArtifact.mutate({ placementId, x, y })}
        />
      </section>

      <EditorZoomControl zoom={zoom} />

      {pendingSwaps.size > 0 ? (
        <div
          className="ite-apply-bar"
          role="region"
          aria-label="Pending changes"
          onPointerDown={(event) => event.stopPropagation()}
        >
          <span className="ite-apply-bar-label">
            {pendingSwaps.size} pending change{pendingSwaps.size > 1 ? 's' : ''}
          </span>
          <Button size="sm" variant="outline" disabled={applying} onClick={() => setPendingSwaps(new Map())}>
            Cancel
          </Button>
          <Button size="sm" disabled={applying} onClick={applyPending}>
            {applying ? 'Applying...' : `Apply${pendingSwaps.size > 1 ? ` ${pendingSwaps.size}` : ''}`}
          </Button>
        </div>
      ) : null}

      <aside
        className="ite-dock"
        aria-label="Tower editor controls"
        onPointerDown={(event) => event.stopPropagation()}
      >
        <header className="ite-bar">
          <div className="ite-bar-left">
            <div className="ite-title-block">
              <p className="editor-eyebrow">Editing</p>
              {isFork ? (
                <h1 className="editor-title">{overview.design.title}</h1>
              ) : (
                <TowerNameField
                  title={overview.design.title}
                  pending={editor.rename.isPending}
                  onRename={(next) => editor.rename.mutate(next)}
                />
              )}
            </div>
          </div>

          <div className="ite-bar-right">
            <Button variant="outline" size="sm" disabled={editor.addStorey.isPending} onClick={addStorey}>
              <Layers className="size-4" aria-hidden="true" />
              Add section
            </Button>
            {isFork ? (
              <span className="editor-fork-note">Private edits to the official tower are visible only to you.</span>
            ) : (
              <>
                <Button size="sm" disabled={editor.publish.isPending} onClick={() => editor.publish.mutate()}>
                  <UploadCloud className="size-4" aria-hidden="true" />
                  {overview.design.status === 'published' ? 'Re-publish' : 'Publish'}
                </Button>
                <Button variant="secondary" size="sm" disabled={editor.share.isPending} onClick={() => editor.share.mutate()}>
                  <Share2 className="size-4" aria-hidden="true" />
                  {editor.share.isPending ? 'Sharing...' : 'Share'}
                </Button>
              </>
            )}
          </div>
        </header>

        <StoreyPicker
          activeStoreyIndex={activeStoreyIndex}
          storeyIndexes={storeyIndexes}
          onSelect={(index) => {
            setSelectedStoreyIndex(index)
            setSelectedPieceId(null)
            setPlacementDraft(null)
          }}
        />

        {shareUrl ? (
          <div className="editor-share-bar">
            <span>Anyone with this link can view your tower:</span>
            <input className="editor-share-input" readOnly value={shareUrl} onFocus={(e) => e.currentTarget.select()} />
            <Button size="sm" variant="outline" onClick={copyShareUrl}>
              <Copy className="size-4" aria-hidden="true" />
              {copied ? 'Copied' : 'Copy'}
            </Button>
          </div>
        ) : null}
        {shareError ? <p className="editor-warning is-error">{shareError}</p> : null}
        {walkRailWarnings.length > 0 ? (
          <p className="editor-warning">
            {walkRailWarnings.length} landing{walkRailWarnings.length > 1 ? 's' : ''} need a walk rail before the companion can stand on them.
          </p>
        ) : null}
        {publishError ? <p className="editor-warning is-error">{publishError}</p> : null}

        <ContextualPieceEditor
          overview={overview}
          editor={editor}
          selectedPieceId={selectedPieceId}
          previewAssetId={previewAssetId}
          placementDraft={placementDraft}
          onPreviewSwap={pickSwap}
          onUploadClick={() => setUploadOpen(true)}
          onPlacementDraft={setPlacementDraft}
        />
      </aside>
    </div>
  )
}

function StoreyPicker({
  storeyIndexes,
  activeStoreyIndex,
  onSelect,
}: {
  storeyIndexes: number[]
  activeStoreyIndex: number | null
  onSelect: (index: number) => void
}) {
  if (storeyIndexes.length <= 1) return null
  return (
    <section className="editor-storey-picker" aria-label="Storey selector">
      {storeyIndexes.map((index, order) => (
        <button
          key={index}
          type="button"
          className={cn('editor-filter-chip', activeStoreyIndex === index && 'is-active')}
          aria-pressed={activeStoreyIndex === index}
          onClick={() => onSelect(index)}
        >
          Storey {order + 1}
        </button>
      ))}
    </section>
  )
}

function ContextualPieceEditor({
  overview,
  editor,
  selectedPieceId,
  previewAssetId,
  placementDraft,
  onPreviewSwap,
  onUploadClick,
  onPlacementDraft,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  selectedPieceId: number | null
  previewAssetId: number | null
  placementDraft: PlacementDraft
  onPreviewSwap: (pieceId: number, assetId: number) => void
  onUploadClick: () => void
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  const piece = selectedPieceId
    ? overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === selectedPieceId) ?? null
    : null

  if (!piece || selectedPieceId === null) {
    return (
      <aside className="editor-inspector" aria-label="Piece editor">
        <p className="editor-inspector-empty">Select a tower piece to change its art or place artifacts.</p>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          Upload asset
        </Button>
      </aside>
    )
  }

  const pieceType = piece.pieceType as TowerPieceType
  const artifacts = overview.artifacts.filter((a) => a.targetInstanceId === piece.instanceId)

  return (
    <aside className="editor-inspector" aria-label="Piece editor">
      <div className="editor-context-head">
        <h2 className="editor-rail-title">{PIECE_TYPE_LABEL[pieceType]}</h2>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          Upload asset
        </Button>
      </div>

      <SkinPanel
        piece={piece}
        pieceId={selectedPieceId}
        editor={editor}
        previewAssetId={previewAssetId}
        onPreviewSwap={onPreviewSwap}
      />

      <TransformPanel piece={piece} pieceId={selectedPieceId} editor={editor} />

      {pieceType === 'section' || pieceType === 'landing' ? (
        <ArtifactPanel
          piece={piece}
          editor={editor}
          artifacts={artifacts}
          placementDraft={placementDraft}
          onPlacementDraft={onPlacementDraft}
        />
      ) : null}
    </aside>
  )
}

function SkinPanel({
  piece,
  pieceId,
  editor,
  previewAssetId,
  onPreviewSwap,
}: {
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  editor: ReturnType<typeof useDesignEditor>
  previewAssetId: number | null
  onPreviewSwap: (pieceId: number, assetId: number) => void
}) {
  const skins = editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === piece.pieceType)

  return (
    <section className="editor-panel">
      <h3 className="editor-panel-title">Piece art</h3>
      <div className="editor-skin-grid">
        {skins.map((descriptor) => {
          const isActive =
            previewAssetId !== null ? descriptor.id === previewAssetId : descriptor.slug === piece.assetSlug
          const thumb = thumbUrl(descriptor)
          const payload: EditorDragPayload = {
            source: 'asset-piece',
            assetId: descriptor.id,
            slug: descriptor.slug,
            pieceType: descriptorPieceType(descriptor) ?? piece.pieceType,
          }
          return (
            <button
              key={descriptor.slug}
              type="button"
              className={cn('editor-skin-cell', `is-${descriptor.source ?? 'official'}`, isActive && 'is-active')}
              draggable
              title={descriptor.label}
              aria-label={descriptor.label}
              aria-pressed={isActive}
              onDragStart={(event) => setDrag(event, payload)}
              onClick={() => {
                if (!isActive) onPreviewSwap(pieceId, descriptor.id)
              }}
            >
              <span className="editor-skin-thumb">
                {thumb ? <img src={thumb} alt="" draggable={false} /> : null}
              </span>
              {isActive ? (
                <span className="editor-skin-check" aria-hidden="true">
                  <Check className="size-3" />
                </span>
              ) : null}
            </button>
          )
        })}
      </div>
    </section>
  )
}

function TransformPanel({
  piece,
  pieceId,
  editor,
}: {
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  editor: ReturnType<typeof useDesignEditor>
}) {
  const transform = readPieceTransform(piece.transform)

  function update(field: keyof PieceTransform, value: number) {
    if (!Number.isFinite(value)) return
    editor.updatePiece.mutate({
      pieceId,
      input: {
        transform: {
          ...(piece.transform ?? {}),
          [field]: value,
        },
      },
    })
  }

  function reset() {
    editor.updatePiece.mutate({ pieceId, input: { transform: {} } })
  }

  return (
    <section className="editor-panel">
      <div className="editor-context-head">
        <h3 className="editor-panel-title">Transform</h3>
        <Button size="sm" variant="outline" onClick={reset}>
          Reset
        </Button>
      </div>
      <div className="editor-transform-grid">
        <label className="editor-control">
          <span className="editor-control-label">X</span>
          <input
            className="upload-input"
            type="number"
            step="1"
            value={transform.x}
            onChange={(event) => update('x', Number(event.target.value))}
          />
        </label>
        <label className="editor-control">
          <span className="editor-control-label">Y</span>
          <input
            className="upload-input"
            type="number"
            step="1"
            value={transform.y}
            onChange={(event) => update('y', Number(event.target.value))}
          />
        </label>
        <label className="editor-control">
          <span className="editor-control-label">Scale</span>
          <input
            className="upload-input"
            type="number"
            min="0.2"
            max="2.5"
            step="0.05"
            value={transform.scale}
            onChange={(event) => update('scale', Number(event.target.value))}
          />
        </label>
        <label className="editor-control">
          <span className="editor-control-label">Rotate</span>
          <input
            className="upload-input"
            type="number"
            min="-45"
            max="45"
            step="1"
            value={transform.rotation}
            onChange={(event) => update('rotation', Number(event.target.value))}
          />
        </label>
      </div>
    </section>
  )
}

function ArtifactPanel({
  piece,
  editor,
  artifacts,
  placementDraft,
  onPlacementDraft,
}: {
  piece: TowerLayoutPieceDescriptor
  editor: ReturnType<typeof useDesignEditor>
  artifacts: ArtifactPlacementDescriptor[]
  placementDraft: PlacementDraft
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  const [role, setRole] = useState<TowerArtifactRole>('normal')
  const [contentId, setContentId] = useState<number | null>(null)
  const allowedRoles: TowerArtifactRole[] = piece.pieceType === 'landing' ? ['normal'] : ['normal', ...INTERACTABLE_ROLES]
  const activeRole = allowedRoles.includes(role) ? role : allowedRoles[0]
  const contentKind = activeRole === 'normal' ? null : (activeRole as ContentKind)
  const contentQuery = useQuery({
    queryKey: contentKind ? queryKeys.authoringContent(contentKind) : ['authoring-content-disabled'],
    queryFn: () => authoringApi.list(contentKind as ContentKind),
    enabled: contentKind !== null,
  })
  const contentOptions = (contentQuery.data?.results ?? []).filter(
    (content) => content.status === 'published' || content.status === 'testable',
  )
  const selectedContentId = contentKind ? contentId ?? contentOptions[0]?.id ?? null : null
  const roleConflict = activeRole !== 'normal' && artifacts.some((artifact) => artifact.role !== 'normal' && artifact.role !== activeRole)

  return (
    <section className="editor-panel">
      <h3 className="editor-panel-title">Artifacts</h3>
      <div className="editor-role-row">
        {allowedRoles.map((value) => (
          <button
            key={value}
            type="button"
            className={cn('editor-filter-chip', activeRole === value && 'is-active')}
            aria-pressed={activeRole === value}
            onClick={() => {
              setRole(value)
              onPlacementDraft(null)
            }}
          >
            {ARTIFACT_ROLE_LABEL[value]}
          </button>
        ))}
      </div>

      {contentKind ? (
        <label className="editor-control">
          <span className="editor-control-label">Content</span>
          <select
            className="upload-input"
            value={selectedContentId ?? ''}
            onChange={(event) => setContentId(Number(event.target.value))}
          >
            {contentOptions.map((content) => (
              <option key={content.id} value={content.id}>
                {content.title}
              </option>
            ))}
          </select>
        </label>
      ) : null}

      {roleConflict ? (
        <p className="editor-warning is-error">This section already has a different interactable artifact type.</p>
      ) : null}

      <div className="editor-artifact-grid">
        {editor.artifactDescriptors.map((descriptor) => {
          const payload: EditorDragPayload = {
            source: 'asset-artifact',
            assetId: descriptor.id,
            slug: descriptor.slug,
            role: activeRole,
            contentDefinitionId: selectedContentId,
          }
          const active =
            placementDraft?.source === 'asset-artifact' &&
            placementDraft.assetId === descriptor.id &&
            placementDraft.role === activeRole
          const disabled = roleConflict || (activeRole !== 'normal' && selectedContentId === null)
          return (
            <button
              type="button"
              key={descriptor.slug}
              className={cn('editor-palette-cell', active && 'is-applicable')}
              draggable={!disabled}
              disabled={disabled}
              title={descriptor.label}
              aria-label={`Place ${descriptor.label}`}
              onClick={() => onPlacementDraft(disabled ? null : payload)}
              onDragStart={(event) => {
                if (!disabled) setDrag(event, payload)
              }}
            >
              <span className="editor-palette-thumb">
                {thumbUrl(descriptor) ? <img src={thumbUrl(descriptor) ?? ''} alt="" draggable={false} /> : null}
              </span>
            </button>
          )
        })}
      </div>

      {placementDraft ? (
        <p className="editor-palette-active">Click the piece or drag the asset onto the exact spot.</p>
      ) : null}

      <PlacedArtifactList artifacts={artifacts} editor={editor} />
    </section>
  )
}

function PlacedArtifactList({
  artifacts,
  editor,
}: {
  artifacts: ArtifactPlacementDescriptor[]
  editor: ReturnType<typeof useDesignEditor>
}) {
  if (!artifacts.length) return <p className="editor-inspector-empty">No artifacts placed on this piece.</p>
  return (
    <ul className="editor-artifact-list">
      {artifacts.map((artifact) => (
        <li key={artifact.id} className="editor-artifact-row">
          <span className="editor-artifact-slug">{artifact.assetSlug}</span>
          <input
            aria-label={`Size ${artifact.assetSlug}`}
            type="range"
            min="0.25"
            max="2.5"
            step="0.05"
            value={artifact.scale}
            onChange={(event) =>
              editor.updateArtifact.mutate({ placementId: artifact.id, scale: Number(event.target.value) })
            }
          />
          <button
            type="button"
            className="editor-icon-btn"
            aria-label="Remove artifact"
            onClick={() => {
              if (typeof artifact.id === 'number') editor.deleteArtifact.mutate(artifact.id)
            }}
          >
            x
          </button>
        </li>
      ))}
    </ul>
  )
}

function EditorZoomControl({ zoom }: { zoom: ZoomPan }) {
  return (
    <div className="tower-zoom-control tower-zoom-control--editor" onPointerDown={(event) => event.stopPropagation()}>
      <input
        aria-label="Editor zoom"
        type="range"
        min="0.45"
        max="2.6"
        step="0.01"
        value={zoom.scale}
        onChange={(event) => zoom.setScale(Number(event.target.value))}
      />
      <button type="button" aria-label="Reset editor view" onClick={zoom.reset}>
        <Maximize2 className="size-4" aria-hidden="true" />
      </button>
    </div>
  )
}

function setDrag(event: React.DragEvent, payload: EditorDragPayload) {
  event.dataTransfer.setData('application/json', JSON.stringify(payload))
  event.dataTransfer.effectAllowed = 'copy'
}

function descriptorPieceType(descriptor: TowerPieceAssetDescriptor): TowerPieceType | undefined {
  return descriptor.piece_type ?? descriptor.tower_piece?.piece_type
}

function thumbUrl(descriptor: { sprites: Record<string, { url: string }> }) {
  const sprite = descriptor.sprites.default ?? Object.values(descriptor.sprites)[0]
  return sprite?.url ? backendUrl(sprite.url) : null
}

type PieceTransform = {
  x: number
  y: number
  scale: number
  rotation: number
}

function readPieceTransform(transform: Record<string, unknown> | undefined): PieceTransform {
  return {
    x: finiteNumber(transform?.x) ?? 0,
    y: finiteNumber(transform?.y) ?? 0,
    scale: positiveNumber(transform?.scale) ?? 1,
    rotation: finiteNumber(transform?.rotation) ?? finiteNumber(transform?.rotate) ?? 0,
  }
}

function uniqueStoreyIndexes(overview: TowerDesignOverview | null) {
  const indexes = new Set<number>()
  for (const piece of overview?.tower_layout.pieces ?? []) {
    if (piece.pieceType !== 'crown') indexes.add(normalizedStoreyIndex(piece))
  }
  return [...indexes].sort((a, b) => a - b)
}

function resolveActiveStoreyIndex(indexes: number[], selected: number | null, preferred: number | null) {
  if (selected !== null && indexes.includes(selected)) return selected
  if (preferred !== null && indexes.includes(preferred)) return preferred
  return indexes[0] ?? null
}

function normalizedStoreyIndex(piece: TowerLayoutPieceDescriptor) {
  return typeof piece.storeyIndex === 'number' ? piece.storeyIndex : 0
}

function finiteNumber(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function positiveNumber(value: unknown) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

function isBounds(value: unknown): value is { width: number; height: number } {
  if (typeof value !== 'object' || value === null) return false
  const maybe = value as { width?: unknown; height?: unknown }
  return Number.isFinite(Number(maybe.width)) && Number.isFinite(Number(maybe.height))
}
