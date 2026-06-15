import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Check, Copy, Layers, Maximize2, PencilLine, Share2, Swords, Trash2, UploadCloud } from 'lucide-react'
import { Link } from 'react-router-dom'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import type { ContentDefinition, ContentKind } from '@/features/authoring/types'
import {
  ARTIFACT_ROLE_LABEL,
  INTERACTABLE_ROLES,
  IDENTITY_PIECE_TRANSFORM,
  PIECE_ROTATION_RANGE,
  PIECE_SCALE_RANGE,
  PIECE_TYPE_LABEL,
  type ArtifactEdit,
  type PieceTransform,
  pieceIdFromInstance,
  pieceTransformIsIdentity,
  pieceTransformToRecord,
  pieceTransformsEqual,
  readPieceTransform,
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
}: {
  designId: number
}) {
  const editor = useDesignEditor(designId)
  const zoom = useZoomPan()
  const [selectedPieceId, setSelectedPieceId] = useState<number | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [placementDraft, setPlacementDraft] = useState<PlacementDraft>(null)
  // Staged, un-applied edits. The canvas renders these immediately; nothing
  // touches the server until the user hits Apply. This is what keeps dragging a
  // piece (or scrubbing a slider) from firing a PATCH on every frame.
  const [pendingSwaps, setPendingSwaps] = useState<Map<number, number>>(new Map())
  const [pieceTransforms, setPieceTransforms] = useState<Map<number, PieceTransform>>(new Map())
  const [artifactEdits, setArtifactEdits] = useState<Map<number | string, ArtifactEdit>>(new Map())
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

  if (editor.isLoading) return <LoadingState label="Opening the editor" variant="page" />
  if (editor.isError || !editor.overview) {
    return <ErrorState title="Could not open this tower" description={(editor.error as Error)?.message ?? ''} />
  }

  const overview = editor.overview
  const isFork = overview.design.origin === 'official_fork'
  const publishError = publishErrorMessage(editor.publish.error)
  const dirtyCount = pendingSwaps.size + pieceTransforms.size + artifactEdits.size
  const pieceCount = overview.tower_layout.pieces.length

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

  function stagePieceTransform(pieceId: number, next: PieceTransform) {
    const piece = overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === pieceId)
    const committed = readPieceTransform(piece?.transform)
    setPieceTransforms((prev) => {
      const map = new Map(prev)
      if (pieceTransformsEqual(next, committed)) map.delete(pieceId)
      else map.set(pieceId, next)
      return map
    })
  }

  function moveArtifact(placementId: number | string, x: number, y: number) {
    const base = overview.artifacts.find((a) => a.id === placementId)
    setArtifactEdits((prev) => {
      const map = new Map(prev)
      const next: ArtifactEdit = { ...(map.get(placementId) ?? {}), x, y }
      if (base && editMatchesBase(next, base)) map.delete(placementId)
      else map.set(placementId, next)
      return map
    })
  }

  function scaleArtifact(artifact: ArtifactPlacementDescriptor, scale: number) {
    setArtifactEdits((prev) => {
      const map = new Map(prev)
      const next: ArtifactEdit = { ...(map.get(artifact.id) ?? {}), scale }
      if (editMatchesBase(next, artifact)) map.delete(artifact.id)
      else map.set(artifact.id, next)
      return map
    })
  }

  function removeArtifact(placementId: number | string) {
    if (typeof placementId === 'number') editor.deleteArtifact.mutate(placementId)
    setArtifactEdits((prev) => {
      if (!prev.has(placementId)) return prev
      const map = new Map(prev)
      map.delete(placementId)
      return map
    })
  }

  function discardChanges() {
    setPendingSwaps(new Map())
    setPieceTransforms(new Map())
    setArtifactEdits(new Map())
  }

  async function applyChanges() {
    setApplying(true)
    try {
      const jobs: Promise<unknown>[] = []
      // Swap + transform on the same piece collapse into one PATCH.
      const pieceIds = new Set<number>([...pendingSwaps.keys(), ...pieceTransforms.keys()])
      for (const pieceId of pieceIds) {
        const input: { piece_asset_id?: number; transform?: Record<string, number> } = {}
        const assetId = pendingSwaps.get(pieceId)
        if (assetId !== undefined) input.piece_asset_id = assetId
        const transform = pieceTransforms.get(pieceId)
        if (transform) input.transform = pieceTransformToRecord(transform)
        jobs.push(editor.updatePiece.mutateAsync({ pieceId, input }))
      }
      for (const [placementId, edit] of artifactEdits) {
        jobs.push(editor.updateArtifact.mutateAsync({ placementId, ...edit }))
      }
      await Promise.all(jobs)
      discardChanges()
    } finally {
      setApplying(false)
    }
  }

  function addStorey() {
    editor.addStorey.mutate(undefined, {
      onSuccess: () => {
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

  const stagedAssetId = selectedPieceId !== null ? pendingSwaps.get(selectedPieceId) ?? null : null
  const selectedPiece = selectedPieceId
    ? overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === selectedPieceId) ?? null
    : null
  const selectedArtifacts = selectedPiece
    ? overview.artifacts.filter((artifact) => artifact.targetInstanceId === selectedPiece.instanceId)
    : []
  const selectedTransform =
    selectedPiece && selectedPieceId !== null
      ? pieceTransforms.get(selectedPieceId) ?? readPieceTransform(selectedPiece.transform)
      : IDENTITY_PIECE_TRANSFORM

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
          pieceTransforms={pieceTransforms}
          artifactEdits={artifactEdits}
          zoomScale={zoom.scale}
          placementDraft={placementDraft}
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
          onMoveArtifact={moveArtifact}
          onTransformPiece={stagePieceTransform}
        />
      </section>

      <EditorZoomControl zoom={zoom} />

      {dirtyCount > 0 ? (
        <div
          className="ite-apply-bar"
          role="region"
          aria-label="Unsaved changes"
          onPointerDown={(event) => event.stopPropagation()}
        >
          <span className="ite-apply-dot" aria-hidden="true" />
          <span className="ite-apply-bar-label">
            {dirtyCount} unsaved change{dirtyCount > 1 ? 's' : ''}
          </span>
          <Button size="sm" variant="ghost" disabled={applying} onClick={discardChanges}>
            Discard
          </Button>
          <Button size="sm" disabled={applying} onClick={applyChanges}>
            {applying ? 'Applying…' : 'Apply changes'}
          </Button>
        </div>
      ) : null}

      <aside
        className="ite-dock"
        aria-label="Tower editor controls"
        onPointerDown={(event) => event.stopPropagation()}
      >
        <header className="ite-head">
          <div className="ite-head-id">
            <p className="ite-eyebrow">Tower editor</p>
            {isFork ? (
              <h1 className="ite-name">{overview.design.title}</h1>
            ) : (
              <TowerNameField
                title={overview.design.title}
                pending={editor.rename.isPending}
                onRename={(next) => editor.rename.mutate(next)}
              />
            )}
            <p className="ite-substat">
              {storeyIndexes.length} storey{storeyIndexes.length === 1 ? '' : 's'} · {pieceCount} piece
              {pieceCount === 1 ? '' : 's'}
            </p>
          </div>

          <div className="ite-head-actions">
            <Button variant="outline" size="sm" disabled={editor.addStorey.isPending} onClick={addStorey}>
              <Layers className="size-4" aria-hidden="true" />
              Add storey
            </Button>
            {isFork ? null : (
              <>
                <Button size="sm" disabled={editor.publish.isPending} onClick={() => editor.publish.mutate()}>
                  <UploadCloud className="size-4" aria-hidden="true" />
                  {overview.design.status === 'published' ? 'Re-publish' : 'Publish'}
                </Button>
                <Button variant="secondary" size="sm" disabled={editor.share.isPending} onClick={() => editor.share.mutate()}>
                  <Share2 className="size-4" aria-hidden="true" />
                  {editor.share.isPending ? 'Sharing…' : 'Share'}
                </Button>
              </>
            )}
          </div>
        </header>

        {isFork ? (
          <p className="ite-note">Private edits to the official tower are visible only to you.</p>
        ) : null}

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
          selectedTransform={selectedTransform}
          stagedAssetId={stagedAssetId}
          artifactEdits={artifactEdits}
          placementDraft={placementDraft}
          onStageSwap={pickSwap}
          onTransformPiece={stagePieceTransform}
          onScaleArtifact={scaleArtifact}
          onRemoveArtifact={removeArtifact}
          onUploadClick={() => setUploadOpen(true)}
          onPlacementDraft={setPlacementDraft}
        />
      </aside>

      <EditorQuestDock artifacts={selectedArtifacts} overview={overview} />
    </div>
  )
}

function EditorQuestDock({
  artifacts,
  overview,
}: {
  artifacts: ArtifactPlacementDescriptor[]
  overview: TowerDesignOverview
}) {
  const questArtifacts = artifacts.filter((artifact) => artifact.role !== 'normal')
  if (!questArtifacts.length) return null
  return (
    <aside className="ite-quest-dock" aria-label="Quest authoring">
      <h2 className="editor-rail-title">Quest levels</h2>
      {questArtifacts.map((artifact) => {
        const content = contentForArtifact(overview, artifact)
        const authorHref = content ? `/authoring/${content.id}` : `/authoring/new/${artifact.role}`
        return (
          <section className="ite-quest-row" key={artifact.id}>
            <div className="ite-quest-main">
              <span className={cn('ite-quest-role', `is-${artifact.role}`)}>{ARTIFACT_ROLE_LABEL[artifact.role]}</span>
              <strong>{content?.title ?? artifact.assetSlug}</strong>
            </div>
            <div className="ite-quest-actions">
              <Link className="ite-quest-action" to={authorHref}>
                <PencilLine className="size-3.5" aria-hidden="true" />
                Author content
              </Link>
              <button className="ite-quest-action" type="button" disabled title="Deferred">
                <Swords className="size-3.5" aria-hidden="true" />
                Customize battle
              </button>
            </div>
          </section>
        )
      })}
    </aside>
  )
}

function ContextualPieceEditor({
  overview,
  editor,
  selectedPieceId,
  selectedTransform,
  stagedAssetId,
  artifactEdits,
  placementDraft,
  onStageSwap,
  onTransformPiece,
  onScaleArtifact,
  onRemoveArtifact,
  onUploadClick,
  onPlacementDraft,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  selectedPieceId: number | null
  selectedTransform: PieceTransform
  stagedAssetId: number | null
  artifactEdits: Map<number | string, ArtifactEdit>
  placementDraft: PlacementDraft
  onStageSwap: (pieceId: number, assetId: number) => void
  onTransformPiece: (pieceId: number, next: PieceTransform) => void
  onScaleArtifact: (artifact: ArtifactPlacementDescriptor, scale: number) => void
  onRemoveArtifact: (placementId: number | string) => void
  onUploadClick: () => void
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  const piece = selectedPieceId
    ? overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === selectedPieceId) ?? null
    : null

  if (!piece || selectedPieceId === null) {
    return (
      <div className="ite-inspector ite-inspector--empty" aria-label="Piece editor">
        <p className="ite-empty">Select a tower piece to swap its art, drop artifacts, or transform it on the canvas.</p>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          <UploadCloud className="size-4" aria-hidden="true" />
          Upload asset
        </Button>
      </div>
    )
  }

  const pieceType = piece.pieceType as TowerPieceType
  const artifacts = overview.artifacts.filter((a) => a.targetInstanceId === piece.instanceId)

  return (
    <div className="ite-inspector" aria-label="Piece editor">
      <div className="ite-section ite-section--head">
        <div>
          <p className="ite-eyebrow">Selected</p>
          <h2 className="ite-section-heading">{PIECE_TYPE_LABEL[pieceType]}</h2>
        </div>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          <UploadCloud className="size-4" aria-hidden="true" />
          Upload
        </Button>
      </div>

      <SkinPanel
        piece={piece}
        pieceId={selectedPieceId}
        editor={editor}
        stagedAssetId={stagedAssetId}
        onStageSwap={onStageSwap}
      />

      <TransformPanel
        pieceId={selectedPieceId}
        transform={selectedTransform}
        onChange={onTransformPiece}
      />

      {pieceType === 'section' || pieceType === 'landing' ? (
        <ArtifactPanel
          piece={piece}
          editor={editor}
          artifacts={artifacts}
          artifactEdits={artifactEdits}
          placementDraft={placementDraft}
          onPlacementDraft={onPlacementDraft}
          onScaleArtifact={onScaleArtifact}
          onRemoveArtifact={onRemoveArtifact}
        />
      ) : null}
    </div>
  )
}

function SkinPanel({
  piece,
  pieceId,
  editor,
  stagedAssetId,
  onStageSwap,
}: {
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  editor: ReturnType<typeof useDesignEditor>
  stagedAssetId: number | null
  onStageSwap: (pieceId: number, assetId: number) => void
}) {
  const skins = editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === piece.pieceType)

  return (
    <section className="ite-section">
      <h3 className="ite-section-title">Piece art</h3>
      <div className="editor-skin-grid">
        {skins.map((descriptor) => {
          const isActive =
            stagedAssetId !== null ? descriptor.id === stagedAssetId : descriptor.slug === piece.assetSlug
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
                if (!isActive) onStageSwap(pieceId, descriptor.id)
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
  pieceId,
  transform,
  onChange,
}: {
  pieceId: number
  transform: PieceTransform
  onChange: (pieceId: number, next: PieceTransform) => void
}) {
  function update(field: keyof PieceTransform, value: number) {
    if (!Number.isFinite(value)) return
    onChange(pieceId, { ...transform, [field]: value })
  }

  const canReset = !pieceTransformIsIdentity(transform)

  return (
    <section className="ite-section">
      <div className="ite-section-head">
        <h3 className="ite-section-title">Transform</h3>
        <button
          type="button"
          className="ite-mini-btn"
          disabled={!canReset}
          onClick={() => onChange(pieceId, IDENTITY_PIECE_TRANSFORM)}
        >
          Reset
        </button>
      </div>
      <p className="ite-hint">Drag the frame on the tower to move, scale, or rotate — or set exact values.</p>
      <div className="ite-field-grid">
        <NumberField label="X" unit="px" value={transform.x} step={1} onCommit={(v) => update('x', v)} />
        <NumberField label="Y" unit="px" value={transform.y} step={1} onCommit={(v) => update('y', v)} />
        <NumberField
          label="Scale"
          unit="×"
          value={transform.scale}
          step={0.05}
          min={PIECE_SCALE_RANGE.min}
          max={PIECE_SCALE_RANGE.max}
          onCommit={(v) => update('scale', v)}
        />
        <NumberField
          label="Rotate"
          unit="°"
          value={transform.rotation}
          step={1}
          min={PIECE_ROTATION_RANGE.min}
          max={PIECE_ROTATION_RANGE.max}
          onCommit={(v) => update('rotation', v)}
        />
      </div>
    </section>
  )
}

function NumberField({
  label,
  unit,
  value,
  step,
  min,
  max,
  onCommit,
}: {
  label: string
  unit?: string
  value: number
  step?: number
  min?: number
  max?: number
  onCommit: (value: number) => void
}) {
  return (
    <label className="ite-field">
      <span className="ite-field-label">
        {label}
        {unit ? <span className="ite-field-unit">{unit}</span> : null}
      </span>
      <input
        className="ite-field-input"
        type="number"
        step={step}
        min={min}
        max={max}
        value={value}
        onChange={(event) => onCommit(Number(event.target.value))}
      />
    </label>
  )
}

function ArtifactPanel({
  piece,
  editor,
  artifacts,
  artifactEdits,
  placementDraft,
  onPlacementDraft,
  onScaleArtifact,
  onRemoveArtifact,
}: {
  piece: TowerLayoutPieceDescriptor
  editor: ReturnType<typeof useDesignEditor>
  artifacts: ArtifactPlacementDescriptor[]
  artifactEdits: Map<number | string, ArtifactEdit>
  placementDraft: PlacementDraft
  onPlacementDraft: (draft: PlacementDraft) => void
  onScaleArtifact: (artifact: ArtifactPlacementDescriptor, scale: number) => void
  onRemoveArtifact: (placementId: number | string) => void
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
    <section className="ite-section">
      <h3 className="ite-section-title">Artifacts</h3>
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
        <label className="ite-field ite-field--wide">
          <span className="ite-field-label">Content</span>
          <select
            className="ite-field-input"
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

      <PlacedArtifactList
        artifacts={artifacts}
        artifactEdits={artifactEdits}
        onScaleArtifact={onScaleArtifact}
        onRemoveArtifact={onRemoveArtifact}
      />
    </section>
  )
}

function PlacedArtifactList({
  artifacts,
  artifactEdits,
  onScaleArtifact,
  onRemoveArtifact,
}: {
  artifacts: ArtifactPlacementDescriptor[]
  artifactEdits: Map<number | string, ArtifactEdit>
  onScaleArtifact: (artifact: ArtifactPlacementDescriptor, scale: number) => void
  onRemoveArtifact: (placementId: number | string) => void
}) {
  if (!artifacts.length) return <p className="ite-empty ite-empty--inline">No artifacts placed on this piece.</p>
  return (
    <ul className="editor-artifact-list">
      {artifacts.map((artifact) => {
        const scale = artifactEdits.get(artifact.id)?.scale ?? artifact.scale
        return (
          <li key={artifact.id} className="editor-artifact-row">
            <span className="editor-artifact-slug">{artifact.assetSlug}</span>
            <input
              aria-label={`Size ${artifact.assetSlug}`}
              type="range"
              min="0.25"
              max="2.5"
              step="0.05"
              value={scale}
              onChange={(event) => onScaleArtifact(artifact, Number(event.target.value))}
            />
            <button
              type="button"
              className="editor-icon-btn"
              aria-label="Remove artifact"
              onClick={() => onRemoveArtifact(artifact.id)}
            >
              <Trash2 className="size-3.5" aria-hidden="true" />
            </button>
          </li>
        )
      })}
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

/** True when every staged field already matches the committed placement. */
function editMatchesBase(edit: ArtifactEdit, base: ArtifactPlacementDescriptor): boolean {
  return (Object.keys(edit) as (keyof ArtifactEdit)[]).every((key) => edit[key] === base[key])
}

function uniqueStoreyIndexes(overview: TowerDesignOverview | null) {
  const indexes = new Set<number>()
  for (const piece of overview?.tower_layout.pieces ?? []) {
    if (piece.pieceType !== 'crown') indexes.add(normalizedStoreyIndex(piece))
  }
  return [...indexes].sort((a, b) => a - b)
}

function normalizedStoreyIndex(piece: TowerLayoutPieceDescriptor) {
  return typeof piece.storeyIndex === 'number' ? piece.storeyIndex : 0
}

function isBounds(value: unknown): value is { width: number; height: number } {
  if (typeof value !== 'object' || value === null) return false
  const maybe = value as { width?: unknown; height?: unknown }
  return Number.isFinite(Number(maybe.width)) && Number.isFinite(Number(maybe.height))
}

function contentForArtifact(
  overview: TowerDesignOverview,
  artifact: ArtifactPlacementDescriptor,
): ContentDefinition | null {
  const id = artifact.contentBinding?.id
  if (id === undefined || artifact.role === 'normal') return null
  const bucket = artifact.role === 'adventure'
    ? overview.content.adventures
    : artifact.role === 'challenge'
      ? overview.content.challenges
      : overview.content.tomes
  return bucket[String(id)] ?? null
}
