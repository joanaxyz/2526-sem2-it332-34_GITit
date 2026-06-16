import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle,
  ArrowLeft,
  Check,
  CheckCircle2,
  Copy,
  Maximize2,
  Minus,
  PencilLine,
  Plus,
  Redo2,
  Share2,
  Trash2,
  Undo2,
  UploadCloud,
} from 'lucide-react'
import { Link } from 'react-router-dom'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import type { ContentDefinition, ContentKind } from '@/features/authoring/types'
import {
  ARTIFACT_ROLE_LABEL,
  ARTIFACT_ROTATION_RANGE,
  ARTIFACT_SCALE_RANGE,
  INTERACTABLE_ROLES,
  IDENTITY_PIECE_TRANSFORM,
  PIECE_ROTATION_RANGE,
  PIECE_SCALE_RANGE,
  PIECE_TYPE_LABEL,
  type ArtifactEdit,
  type ArtifactTransform,
  type PieceTransform,
  clampNumber,
  pieceIdFromInstance,
  pieceTransformIsIdentity,
  pieceTransformToRecord,
  pieceTransformsEqual,
  readArtifactTransform,
  readPieceTransform,
} from '@/features/tower-designs/editorUtils'
import {
  buildSectionStatuses,
  validateDesign,
  type DesignIssue,
  type SectionStatus,
} from '@/features/tower-designs/editorValidation'
import {
  EditorStorey,
  type EditorDragPayload,
  type PlacementDraft,
} from '@/features/tower-designs/components/EditorStorey'
import { UploadAssetDialog } from '@/features/tower-designs/components/UploadAssetDialog'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { useDesignEditor } from '@/features/tower-designs/hooks/useDesignEditor'
import { useStagedEdits } from '@/features/tower-designs/hooks/useStagedEdits'
import { pieceHasWalkRail } from '@/features/tower-map/components/towerPieceData'
import { useZoomPan, type ZoomPan } from '@/features/tower-map/editor/useZoomPan'
import { backendUrl } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import type {
  TowerArtifactAssetDescriptor,
  TowerArtifactRole,
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'
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

function apiErrorMessage(error: unknown): string | null {
  if (!(error instanceof ApiError)) return error ? 'Something went wrong.' : null
  const payload = error.payload as
    | { detail?: string; validation_errors?: { message: string }[]; [key: string]: unknown }
    | null
  if (payload?.validation_errors?.length) {
    return payload.validation_errors.map((row) => row.message).join(' ')
  }
  if (payload?.detail) return payload.detail
  // DRF field errors come back as { field: ["msg"] }; surface the first.
  if (payload && typeof payload === 'object') {
    for (const value of Object.values(payload)) {
      if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
      if (typeof value === 'string') return value
    }
  }
  return error.message
}

export function InTowerEditor({ designId, onExit }: { designId: number; onExit?: () => void }) {
  const editor = useDesignEditor(designId)
  const zoom = useZoomPan()
  const staged = useStagedEdits()
  const [selectedPieceId, setSelectedPieceId] = useState<number | null>(null)
  const [selectedArtifactId, setSelectedArtifactId] = useState<number | string | null>(null)
  const [activeStorey, setActiveStorey] = useState<number | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [placementDraft, setPlacementDraft] = useState<PlacementDraft>(null)
  const [applying, setApplying] = useState(false)
  const [toast, setToast] = useState<{ kind: 'error' | 'info'; message: string } | null>(null)
  const [showIssues, setShowIssues] = useState(false)
  const toastTimer = useRef<number | undefined>(undefined)

  const { pendingSwaps, pieceTransforms, artifactEdits } = staged

  const pieceDescriptorById = useMemo(
    () => new Map(editor.pieceDescriptors.map((d) => [d.id, d])),
    [editor.pieceDescriptors],
  )
  const walkRailWarnings = useMemo(() => {
    if (!editor.overview) return []
    return editor.overview.tower_layout.pieces
      .filter((p) => p.pieceType === 'landing')
      .filter((p) => !pieceHasWalkRail(editor.pieceDescriptorBySlug[p.assetSlug]))
  }, [editor.overview, editor.pieceDescriptorBySlug])
  const storeyIndexes = useMemo(() => uniqueStoreyIndexes(editor.overview), [editor.overview])
  const sectionStatuses = useMemo<Map<string, SectionStatus>>(
    () => (editor.overview ? buildSectionStatuses(editor.overview) : new Map()),
    [editor.overview],
  )
  const issues = useMemo<DesignIssue[]>(
    () => (editor.overview ? validateDesign(editor.overview) : []),
    [editor.overview],
  )

  function flashToast(message: string, kind: 'error' | 'info' = 'error') {
    setToast({ kind, message })
    window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 3600)
  }

  // Ctrl/Cmd+Z undo, Ctrl+Shift+Z / Ctrl+Y redo. Defer to native text undo while
  // a form control is focused (renaming, scrubbing a number field).
  const { undo: undoEdit, redo: redoEdit } = staged
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (!(event.ctrlKey || event.metaKey)) return
      const tag = (event.target as HTMLElement | null)?.tagName
      if (tag && /^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return
      const key = event.key.toLowerCase()
      if (key === 'z') {
        event.preventDefault()
        if (event.shiftKey) redoEdit()
        else undoEdit()
      } else if (key === 'y') {
        event.preventDefault()
        redoEdit()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [undoEdit, redoEdit])

  useEffect(() => () => window.clearTimeout(toastTimer.current), [])

  // The canvas edits one storey at a time. Fall back to the first storey when the
  // tracked tab no longer exists (e.g. after deleting the storey's last piece).
  const activeStoreyIndex =
    activeStorey !== null && storeyIndexes.includes(activeStorey) ? activeStorey : storeyIndexes[0] ?? null

  if (editor.isLoading) return <LoadingState label="Opening the editor" variant="page" />
  if (editor.isError || !editor.overview) {
    return <ErrorState title="Could not open this tower" description={(editor.error as Error)?.message ?? ''} />
  }

  const overview = editor.overview
  const isFork = overview.design.origin === 'official_fork'
  const publishError = apiErrorMessage(editor.publish.error) ?? apiErrorMessage(editor.share.error)
  const shared = editor.share.data
  const shareUrl = shared?.share_path ? `${window.location.origin}${shared.share_path}` : null
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
    staged.commit((state) => {
      const next = new Map(state.pendingSwaps)
      if (assetId === committedId) next.delete(pieceId)
      else next.set(pieceId, assetId)
      return { ...state, pendingSwaps: next }
    })
    staged.endGesture()
  }

  function stagePieceTransform(pieceId: number, next: PieceTransform) {
    const piece = overview.tower_layout.pieces.find((p) => pieceIdFromInstance(p.instanceId) === pieceId)
    const committed = readPieceTransform(piece?.transform)
    staged.commit((state) => {
      const map = new Map(state.pieceTransforms)
      if (pieceTransformsEqual(next, committed)) map.delete(pieceId)
      else map.set(pieceId, next)
      return { ...state, pieceTransforms: map }
    }, `piece:${pieceId}`)
  }

  function moveArtifact(placementId: number | string, x: number, y: number) {
    const base = overview.artifacts.find((a) => a.id === placementId)
    staged.commit((state) => {
      const map = new Map(state.artifactEdits)
      const next = { ...(map.get(placementId) ?? {}), x, y }
      if (base && editMatchesBase(next, base)) map.delete(placementId)
      else map.set(placementId, next)
      return { ...state, artifactEdits: map }
    }, `artifact:${placementId}`)
  }

  function transformArtifact(artifact: ArtifactPlacementDescriptor, transform: ArtifactTransform) {
    staged.commit((state) => {
      const map = new Map(state.artifactEdits)
      const next = {
        ...(map.get(artifact.id) ?? {}),
        x: transform.x,
        y: transform.y,
        scale: transform.scale,
        rotation: transform.rotation,
        width: transform.width,
        height: transform.height,
      }
      if (editMatchesBase(next, artifact)) map.delete(artifact.id)
      else map.set(artifact.id, next)
      return { ...state, artifactEdits: map }
    }, `artifact:${artifact.id}`)
  }

  function removeArtifact(placementId: number | string) {
    if (typeof placementId === 'number') {
      editor.deleteArtifact.mutate(placementId, {
        onError: (error) => flashToast(apiErrorMessage(error) ?? 'Could not remove artifact.'),
      })
    }
    setSelectedArtifactId((id) => (id === placementId ? null : id))
    staged.commit((state) => {
      if (!state.artifactEdits.has(placementId)) return state
      const map = new Map(state.artifactEdits)
      map.delete(placementId)
      return { ...state, artifactEdits: map }
    })
    staged.endGesture()
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
      // Clear the overlay only after fresh layout lands, so the canvas never
      // flashes back to the pre-apply transform between commit and refetch.
      await editor.refetchLayout()
      staged.reset()
    } catch (error) {
      flashToast(apiErrorMessage(error) ?? 'Could not apply changes.')
    } finally {
      setApplying(false)
    }
  }

  function selectStorey(storeyIndex: number) {
    setActiveStorey(storeyIndex)
    setSelectedPieceId(null)
    setSelectedArtifactId(null)
    setPlacementDraft(null)
  }

  function addStorey() {
    editor.addStorey.mutate(undefined, {
      onSuccess: (data) => {
        // Jump straight to the freshly raised storey so the new section is in view.
        setActiveStorey(data.added_storey_index)
        setSelectedPieceId(null)
        setSelectedArtifactId(null)
        setPlacementDraft(null)
      },
      onError: (error) => flashToast(apiErrorMessage(error) ?? 'Could not raise a storey.'),
    })
  }

  function focusIssue(issue: DesignIssue) {
    setActiveStorey(issue.storeyIndex)
    setSelectedPieceId(pieceIdFromInstance(issue.instanceId))
    setSelectedArtifactId(null)
    setPlacementDraft(null)
    setShowIssues(false)
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
  const selectedArtifact = selectedArtifactId !== null
    ? overview.artifacts.find((artifact) => artifact.id === selectedArtifactId) ?? null
    : null
  const selectedTransform =
    selectedPiece && selectedPieceId !== null
      ? pieceTransforms.get(selectedPieceId) ?? readPieceTransform(selectedPiece.transform)
      : IDENTITY_PIECE_TRANSFORM
  const selectedArtifactTransform = selectedArtifact
    ? readArtifactTransform(selectedArtifact, artifactEdits.get(selectedArtifact.id))
    : null
  const selectedSectionStatus =
    selectedPiece?.pieceType === 'section' ? sectionStatuses.get(selectedPiece.instanceId) ?? null : null

  return (
    <div className="in-tower-editor">
      {uploadOpen ? <UploadAssetDialog onClose={() => setUploadOpen(false)} /> : null}

      <EditorCommandBar
        overview={overview}
        isFork={isFork}
        onExit={onExit}
        renamePending={editor.rename.isPending}
        onRename={(next) => editor.rename.mutate(next)}
        storeyCount={storeyIndexes.length}
        pieceCount={pieceCount}
        storeyIndexes={storeyIndexes}
        activeStoreyIndex={activeStoreyIndex}
        addingStorey={editor.addStorey.isPending}
        onSelectStorey={selectStorey}
        onAddStorey={addStorey}
        zoom={zoom}
        canUndo={staged.canUndo}
        canRedo={staged.canRedo}
        onUndo={staged.undo}
        onRedo={staged.redo}
        issueCount={issues.length}
        showIssues={showIssues}
        onToggleIssues={() => setShowIssues((v) => !v)}
        publishPending={editor.publish.isPending}
        sharePending={editor.share.isPending}
        onPublish={() => editor.publish.mutate()}
        onShare={() => editor.share.mutate()}
      />

      <EditorStatusLine
        isFork={isFork}
        issues={issues}
        showIssues={showIssues}
        onFocusIssue={focusIssue}
        walkRailCount={walkRailWarnings.length}
        publishError={publishError}
        shareUrl={shareUrl}
        copied={copied}
        onCopyShare={copyShareUrl}
      />

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
          selectedArtifactId={selectedArtifactId}
          activeStoreyIndex={activeStoreyIndex}
          pendingSwaps={pendingSwaps}
          pieceTransforms={pieceTransforms}
          artifactEdits={artifactEdits}
          zoomScale={zoom.scale}
          placementDraft={placementDraft}
          onSelectPiece={(pieceId) => {
            setSelectedPieceId(pieceId)
            setSelectedArtifactId(null)
            setPlacementDraft(null)
          }}
          onSelectArtifact={(artifactId, pieceId) => {
            setSelectedArtifactId(artifactId)
            setSelectedPieceId(pieceId)
            setPlacementDraft(null)
          }}
          onSwapAsset={pickSwap}
          onPlaceArtifact={(pieceId, assetId, role, contentDefinitionId, x, y) => {
            const size = artifactSize(assetId)
            editor.placeArtifact.mutate(
              {
                target_piece_instance_id: pieceId,
                artifact_asset_id: assetId,
                role,
                content_definition_id: contentDefinitionId ?? null,
                x,
                y,
                width: size.width,
                height: size.height,
              },
              { onError: (error) => flashToast(apiErrorMessage(error) ?? 'Could not place artifact.') },
            )
            setPlacementDraft(null)
          }}
          onMoveArtifact={moveArtifact}
          onTransformArtifact={(placementId, next) => {
            const artifact = overview.artifacts.find((item) => item.id === placementId)
            if (artifact) transformArtifact(artifact, next)
          }}
          onTransformPiece={stagePieceTransform}
          onGestureEnd={staged.endGesture}
          onRejectPlacement={(reason) => flashToast(reason)}
        />
      </section>

      <aside className="ite-rail ite-rail--library" aria-label="Asset library" onPointerDown={(e) => e.stopPropagation()}>
        <StoragePanel
          overview={overview}
          editor={editor}
          placementDraft={placementDraft}
          selectedSectionStatus={selectedSectionStatus}
          onUploadClick={() => setUploadOpen(true)}
          onPlacementDraft={setPlacementDraft}
        />
      </aside>

      <aside className="ite-rail ite-rail--inspector" aria-label="Inspector" onPointerDown={(e) => e.stopPropagation()}>
        <PropertiesPanel
          overview={overview}
          editor={editor}
          selectedPieceId={selectedPieceId}
          selectedPiece={selectedPiece}
          selectedArtifact={selectedArtifact}
          selectedTransform={selectedTransform}
          selectedArtifactTransform={selectedArtifactTransform}
          selectedSectionStatus={selectedSectionStatus}
          stagedAssetId={stagedAssetId}
          onStageSwap={pickSwap}
          onTransformPiece={stagePieceTransform}
          onTransformArtifact={(artifact, next) => transformArtifact(artifact, next)}
          onGestureEnd={staged.endGesture}
          onRemovePiece={(pieceId) => {
            editor.deletePiece.mutate(pieceId, {
              onError: (error) => flashToast(apiErrorMessage(error) ?? 'Could not delete piece.'),
            })
            setSelectedPieceId(null)
            setSelectedArtifactId(null)
          }}
          onRemoveArtifact={removeArtifact}
          onUploadClick={() => setUploadOpen(true)}
        />
      </aside>

      {toast ? (
        <div className={cn('ite-toast', toast.kind === 'error' && 'is-error')} role="status" aria-live="polite">
          <AlertTriangle className="size-4" aria-hidden="true" />
          <span>{toast.message}</span>
        </div>
      ) : null}

      {staged.dirtyCount > 0 ? (
        <div
          className="ite-apply-bar"
          role="region"
          aria-label="Unsaved changes"
          onPointerDown={(event) => event.stopPropagation()}
        >
          <span className="ite-apply-dot" aria-hidden="true" />
          <span className="ite-apply-bar-label">
            {staged.dirtyCount} unsaved change{staged.dirtyCount > 1 ? 's' : ''}
          </span>
          <Button size="sm" variant="ghost" disabled={applying} onClick={() => staged.reset()}>
            Discard
          </Button>
          <Button size="sm" disabled={applying} onClick={applyChanges}>
            {applying ? 'Applying…' : 'Apply changes'}
          </Button>
        </div>
      ) : null}
    </div>
  )
}

// --- Command bar ------------------------------------------------------------
// One glass blade across the top: identity (left), storey switcher (centre),
// undo/redo · zoom · validation · publish/share (right). Replaces the old
// header-in-dock + floating storey pill + floating zoom puck.
function EditorCommandBar({
  overview,
  isFork,
  onExit,
  renamePending,
  onRename,
  storeyCount,
  pieceCount,
  storeyIndexes,
  activeStoreyIndex,
  addingStorey,
  onSelectStorey,
  onAddStorey,
  zoom,
  canUndo,
  canRedo,
  onUndo,
  onRedo,
  issueCount,
  showIssues,
  onToggleIssues,
  publishPending,
  sharePending,
  onPublish,
  onShare,
}: {
  overview: TowerDesignOverview
  isFork: boolean
  onExit?: () => void
  renamePending: boolean
  onRename: (next: string) => void
  storeyCount: number
  pieceCount: number
  storeyIndexes: number[]
  activeStoreyIndex: number | null
  addingStorey: boolean
  onSelectStorey: (storeyIndex: number) => void
  onAddStorey: () => void
  zoom: ZoomPan
  canUndo: boolean
  canRedo: boolean
  onUndo: () => void
  onRedo: () => void
  issueCount: number
  showIssues: boolean
  onToggleIssues: () => void
  publishPending: boolean
  sharePending: boolean
  onPublish: () => void
  onShare: () => void
}) {
  return (
    <header className="ite-cmdbar" onPointerDown={(e) => e.stopPropagation()}>
      {onExit ? (
        <button
          type="button"
          className="ite-iconbtn ite-cmd-exit"
          aria-label="Return to tower"
          title="Return to tower"
          onClick={onExit}
        >
          <ArrowLeft className="size-4" aria-hidden="true" />
        </button>
      ) : null}
      <div className="ite-cmd-id">
        <p className="ite-eyebrow">Tower editor</p>
        {isFork ? (
          <h1 className="ite-name">{overview.design.title}</h1>
        ) : (
          <TowerNameField title={overview.design.title} pending={renamePending} onRename={onRename} />
        )}
        <p className="ite-substat">
          {storeyCount} storey{storeyCount === 1 ? '' : 's'} · {pieceCount} piece{pieceCount === 1 ? '' : 's'}
        </p>
      </div>

      <StoreyTabs
        storeyIndexes={storeyIndexes}
        activeStoreyIndex={activeStoreyIndex}
        adding={addingStorey}
        onSelect={onSelectStorey}
        onAdd={onAddStorey}
      />

      <div className="ite-cmd-actions">
        <div className="ite-cmd-cluster" role="group" aria-label="History">
          <button type="button" className="ite-iconbtn" disabled={!canUndo} aria-label="Undo (Ctrl+Z)" title="Undo (Ctrl+Z)" onClick={onUndo}>
            <Undo2 className="size-4" aria-hidden="true" />
          </button>
          <button type="button" className="ite-iconbtn" disabled={!canRedo} aria-label="Redo (Ctrl+Shift+Z)" title="Redo (Ctrl+Shift+Z)" onClick={onRedo}>
            <Redo2 className="size-4" aria-hidden="true" />
          </button>
        </div>

        <div className="ite-cmd-cluster ite-zoom" role="group" aria-label="Zoom">
          <button type="button" className="ite-iconbtn" aria-label="Zoom out" onClick={zoom.zoomOut}>
            <Minus className="size-4" aria-hidden="true" />
          </button>
          <span className="ite-zoom-value" aria-live="off">{Math.round(zoom.scale * 100)}%</span>
          <button type="button" className="ite-iconbtn" aria-label="Zoom in" onClick={zoom.zoomIn}>
            <Plus className="size-4" aria-hidden="true" />
          </button>
          <button type="button" className="ite-iconbtn" aria-label="Reset view" title="Reset view" onClick={zoom.reset}>
            <Maximize2 className="size-4" aria-hidden="true" />
          </button>
        </div>

        <button
          type="button"
          className={cn('ite-valchip', issueCount === 0 ? 'is-ok' : 'is-warn', showIssues && 'is-open')}
          aria-pressed={showIssues}
          aria-label={issueCount === 0 ? 'No publish issues' : `${issueCount} publish issue${issueCount > 1 ? 's' : ''}`}
          onClick={onToggleIssues}
        >
          {issueCount === 0 ? (
            <CheckCircle2 className="size-4" aria-hidden="true" />
          ) : (
            <AlertTriangle className="size-4" aria-hidden="true" />
          )}
          <span>{issueCount === 0 ? 'Ready' : `${issueCount} issue${issueCount > 1 ? 's' : ''}`}</span>
        </button>

        {isFork ? null : (
          <>
            <Button variant="secondary" size="sm" disabled={sharePending} onClick={onShare}>
              <Share2 className="size-4" aria-hidden="true" />
              {sharePending ? 'Sharing…' : 'Share'}
            </Button>
            <Button size="sm" disabled={publishPending} onClick={onPublish}>
              <UploadCloud className="size-4" aria-hidden="true" />
              {overview.design.status === 'published' ? 'Re-publish' : 'Publish'}
            </Button>
          </>
        )}
      </div>
    </header>
  )
}

// Storey switcher: one tab per storey (the canvas edits a single storey at a
// time) plus a trailing button that raises a new storey. Labels are 1-based by
// stacking order, independent of the raw storey_index values.
function StoreyTabs({
  storeyIndexes,
  activeStoreyIndex,
  adding,
  onSelect,
  onAdd,
}: {
  storeyIndexes: number[]
  activeStoreyIndex: number | null
  adding: boolean
  onSelect: (storeyIndex: number) => void
  onAdd: () => void
}) {
  return (
    <div className="ite-cmd-storeys" role="tablist" aria-label="Tower storeys">
      {storeyIndexes.map((storeyIndex, order) => {
        const active = storeyIndex === activeStoreyIndex
        return (
          <button
            key={storeyIndex}
            type="button"
            role="tab"
            aria-selected={active}
            className={cn('ite-storey-tab', active && 'is-active')}
            onClick={() => onSelect(storeyIndex)}
          >
            Storey {order + 1}
          </button>
        )
      })}
      <button
        type="button"
        className="ite-storey-tab ite-storey-tab--add"
        disabled={adding}
        aria-label="Add storey"
        onClick={onAdd}
      >
        <Plus className="size-4" aria-hidden="true" />
        {adding ? 'Adding…' : 'Storey'}
      </button>
    </div>
  )
}

// --- Status line ------------------------------------------------------------
// Drops below the command bar only when there's something to say: the share
// link, publish errors, walk-rail warnings, or the expanded issue list.
function EditorStatusLine({
  isFork,
  issues,
  showIssues,
  onFocusIssue,
  walkRailCount,
  publishError,
  shareUrl,
  copied,
  onCopyShare,
}: {
  isFork: boolean
  issues: DesignIssue[]
  showIssues: boolean
  onFocusIssue: (issue: DesignIssue) => void
  walkRailCount: number
  publishError: string | null
  shareUrl: string | null
  copied: boolean
  onCopyShare: () => void
}) {
  const hasContent =
    (showIssues && issues.length > 0) || walkRailCount > 0 || !!publishError || !!shareUrl || isFork
  if (!hasContent) return null
  return (
    <div className="ite-statusline" onPointerDown={(e) => e.stopPropagation()}>
      {isFork ? (
        <p className="ite-status-msg">Private edits to the official tower are visible only to you.</p>
      ) : null}
      {showIssues && issues.length > 0 ? (
        <ul className="ite-issue-list">
          {issues.map((issue) => (
            <li key={issue.id}>
              <button type="button" className="ite-issue" onClick={() => onFocusIssue(issue)}>
                <AlertTriangle className="size-3.5" aria-hidden="true" />
                <span className="ite-issue-storey">Storey {issue.storeyIndex + 1}</span>
                <span className="ite-issue-msg">{issue.message}</span>
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {walkRailCount > 0 ? (
        <p className="ite-status-msg is-warn">
          {walkRailCount} landing{walkRailCount > 1 ? 's' : ''} need a walk rail before the companion can stand on them.
        </p>
      ) : null}
      {publishError ? <p className="ite-status-msg is-error">{publishError}</p> : null}
      {shareUrl ? (
        <div className="editor-share-bar">
          <span>Anyone with this link can view your tower:</span>
          <input className="editor-share-input" readOnly value={shareUrl} onFocus={(e) => e.currentTarget.select()} />
          <Button size="sm" variant="outline" onClick={onCopyShare}>
            <Copy className="size-4" aria-hidden="true" />
            {copied ? 'Copied' : 'Copy'}
          </Button>
        </div>
      ) : null}
    </div>
  )
}

// --- Library (left rail) ----------------------------------------------------
function StoragePanel({
  overview,
  editor,
  placementDraft,
  selectedSectionStatus,
  onUploadClick,
  onPlacementDraft,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  placementDraft: PlacementDraft
  selectedSectionStatus: SectionStatus | null
  onUploadClick: () => void
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  const [role, setRole] = useState<TowerArtifactRole>('adventure')
  const [contentId, setContentId] = useState<number | null>(null)
  const contentKind = role as ContentKind
  const contentQuery = useQuery({
    queryKey: queryKeys.authoringContent(contentKind),
    queryFn: () => authoringApi.list(contentKind),
  })
  const contentOptions = (contentQuery.data?.results ?? []).filter(
    (content) => content.status === 'published' || content.status === 'testable',
  )
  const selectedContentId = contentId ?? contentOptions[0]?.id ?? null
  const spires = editor.pieceDescriptors.filter((descriptor) => descriptorPieceType(descriptor) === 'crown')
  const sections = editor.pieceDescriptors.filter((descriptor) => descriptorPieceType(descriptor) === 'section')
  const landings = editor.pieceDescriptors.filter((descriptor) => descriptorPieceType(descriptor) === 'landing')

  return (
    <div className="ite-inspector" aria-label="Asset library">
      <div className="ite-section ite-section--head">
        <div>
          <p className="ite-eyebrow">Library</p>
          <h2 className="ite-section-heading">{overview.tower_layout.pieces.length} assets placed</h2>
        </div>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          <UploadCloud className="size-4" aria-hidden="true" />
          Upload
        </Button>
      </div>

      <StoragePieceShelf title="Spire" descriptors={spires} />
      <StoragePieceShelf title="Sections" descriptors={sections} />
      <StoragePieceShelf title="Landings" descriptors={landings} />
      <StorageArtifactShelf
        title="Normal artifacts"
        descriptors={editor.artifactDescriptors}
        payloadFor={(descriptor) => ({
          source: 'asset-artifact',
          assetId: descriptor.id,
          slug: descriptor.slug,
          role: 'normal',
        })}
        active={placementDraft}
        onPlacementDraft={onPlacementDraft}
      />
      <section className="ite-section">
        <div className="ite-section-head">
          <h3 className="ite-section-title">Interactive artifacts</h3>
          <span className="ite-rule-pill">{role === 'challenge' ? 'set of 3' : 'one / section'}</span>
        </div>
        <p className="ite-hint">
          {role === 'challenge'
            ? 'A section holds the full Easy → Medium → Hard chain — exactly three challenges.'
            : 'A section holds a single interactive artifact.'}
        </p>
        {selectedSectionStatus ? <SectionStatusLine status={selectedSectionStatus} /> : null}
        <div className="editor-role-row">
          {INTERACTABLE_ROLES.map((value) => (
            <button
              key={value}
              type="button"
              className={cn('editor-filter-chip', role === value && 'is-active')}
              aria-pressed={role === value}
              onClick={() => {
                setRole(value)
                setContentId(null)
                onPlacementDraft(null)
              }}
            >
              {ARTIFACT_ROLE_LABEL[value]}
            </button>
          ))}
        </div>
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
        {contentOptions.length === 0 ? (
          <p className="ite-empty ite-empty--inline">Publish or test content before placing an interactive artifact.</p>
        ) : null}
        <StorageArtifactGrid
          descriptors={editor.artifactDescriptors}
          disabled={selectedContentId === null}
          active={placementDraft}
          payloadFor={(descriptor) => ({
            source: 'asset-artifact',
            assetId: descriptor.id,
            slug: descriptor.slug,
            role,
            contentDefinitionId: selectedContentId,
          })}
          onPlacementDraft={onPlacementDraft}
        />
      </section>
      {placementDraft ? <p className="editor-palette-active">Drag to a tower piece, or click the destination piece.</p> : null}
    </div>
  )
}

function StoragePieceShelf({
  title,
  descriptors,
}: {
  title: string
  descriptors: TowerPieceAssetDescriptor[]
}) {
  return (
    <section className="ite-section">
      <div className="ite-section-head">
        <h3 className="ite-section-title">{title}</h3>
        <span className="ite-rule-pill">{descriptors.length}</span>
      </div>
      <div className="editor-skin-grid">
        {descriptors.map((descriptor) => {
          const payload: EditorDragPayload = {
            source: 'asset-piece',
            assetId: descriptor.id,
            slug: descriptor.slug,
            pieceType: descriptorPieceType(descriptor) ?? 'section',
          }
          const thumb = thumbUrl(descriptor)
          return (
            <button
              key={descriptor.slug}
              type="button"
              className={cn('editor-skin-cell', `is-${descriptor.source ?? 'official'}`)}
              draggable
              title={descriptor.label}
              aria-label={`Drag ${descriptor.label}`}
              onDragStart={(event) => setDrag(event, payload)}
            >
              <span className="editor-skin-thumb">
                {thumb ? <img src={thumb} alt="" draggable={false} /> : null}
              </span>
            </button>
          )
        })}
      </div>
    </section>
  )
}

function StorageArtifactShelf({
  title,
  descriptors,
  payloadFor,
  active,
  onPlacementDraft,
}: {
  title: string
  descriptors: TowerArtifactAssetDescriptor[]
  payloadFor: (descriptor: TowerArtifactAssetDescriptor) => Exclude<PlacementDraft, null>
  active: PlacementDraft
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  return (
    <section className="ite-section">
      <div className="ite-section-head">
        <h3 className="ite-section-title">{title}</h3>
        <span className="ite-rule-pill">{descriptors.length}</span>
      </div>
      <StorageArtifactGrid
        descriptors={descriptors}
        payloadFor={payloadFor}
        active={active}
        onPlacementDraft={onPlacementDraft}
      />
    </section>
  )
}

function StorageArtifactGrid({
  descriptors,
  payloadFor,
  active,
  disabled = false,
  onPlacementDraft,
}: {
  descriptors: TowerArtifactAssetDescriptor[]
  payloadFor: (descriptor: TowerArtifactAssetDescriptor) => Exclude<PlacementDraft, null>
  active: PlacementDraft
  disabled?: boolean
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  return (
    <div className="editor-artifact-grid">
      {descriptors.map((descriptor) => {
        const payload = payloadFor(descriptor)
        const isActive =
          payload.source === 'asset-artifact' &&
          active?.source === 'asset-artifact' &&
          active.assetId === payload.assetId &&
          active.role === payload.role
        return (
          <button
            type="button"
            key={`${payload.role}-${descriptor.slug}`}
            className={cn('editor-palette-cell', isActive && 'is-applicable')}
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
  )
}

// --- Inspector (right rail) -------------------------------------------------
function PropertiesPanel({
  overview,
  editor,
  selectedPieceId,
  selectedPiece,
  selectedArtifact,
  selectedTransform,
  selectedArtifactTransform,
  selectedSectionStatus,
  stagedAssetId,
  onStageSwap,
  onTransformPiece,
  onTransformArtifact,
  onGestureEnd,
  onRemovePiece,
  onRemoveArtifact,
  onUploadClick,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  selectedPieceId: number | null
  selectedPiece: TowerLayoutPieceDescriptor | null
  selectedArtifact: ArtifactPlacementDescriptor | null
  selectedTransform: PieceTransform
  selectedArtifactTransform: ArtifactTransform | null
  selectedSectionStatus: SectionStatus | null
  stagedAssetId: number | null
  onStageSwap: (pieceId: number, assetId: number) => void
  onTransformPiece: (pieceId: number, next: PieceTransform) => void
  onTransformArtifact: (artifact: ArtifactPlacementDescriptor, next: ArtifactTransform) => void
  onGestureEnd: () => void
  onRemovePiece: (pieceId: number) => void
  onRemoveArtifact: (placementId: number | string) => void
  onUploadClick: () => void
}) {
  if (selectedArtifact && selectedArtifactTransform) {
    const content = contentForArtifact(overview, selectedArtifact)
    const authorHref = content ? `/authoring/${content.id}` : `/authoring/new/${selectedArtifact.role}`
    return (
      <div className="ite-inspector" aria-label="Artifact properties">
        <div className="ite-section ite-section--head">
          <div>
            <p className="ite-eyebrow">Artifact</p>
            <h2 className="ite-section-heading">{ARTIFACT_ROLE_LABEL[selectedArtifact.role]}</h2>
          </div>
          <button
            type="button"
            className="editor-danger-icon"
            aria-label="Remove artifact"
            onClick={() => onRemoveArtifact(selectedArtifact.id)}
          >
            <Trash2 className="size-3.5" aria-hidden="true" />
          </button>
        </div>
        <ArtifactTransformPanel
          artifact={selectedArtifact}
          transform={selectedArtifactTransform}
          onChange={(next) => onTransformArtifact(selectedArtifact, next)}
          onGestureEnd={onGestureEnd}
        />
        {selectedArtifact.role !== 'normal' ? (
          <section className="ite-section">
            <h3 className="ite-section-title">Content</h3>
            <Link className="ite-quest-action" to={authorHref}>
              <PencilLine className="size-3.5" aria-hidden="true" />
              {content ? `Author ${content.title}` : 'Author content'}
            </Link>
          </section>
        ) : null}
      </div>
    )
  }

  if (!selectedPiece || selectedPieceId === null) {
    return (
      <div className="ite-inspector ite-inspector--empty" aria-label="Inspector">
        <p className="ite-empty">Select a tower piece to edit its properties, or pick an artifact to transform it.</p>
        <Button size="sm" variant="outline" onClick={onUploadClick}>
          <UploadCloud className="size-4" aria-hidden="true" />
          Upload asset
        </Button>
      </div>
    )
  }

  const pieceType = selectedPiece.pieceType as TowerPieceType

  return (
    <div className="ite-inspector" aria-label="Piece properties">
      <div className="ite-section ite-section--head">
        <div>
          <p className="ite-eyebrow">Piece</p>
          <h2 className="ite-section-heading">{PIECE_TYPE_LABEL[pieceType]}</h2>
        </div>
        <button
          type="button"
          className="editor-danger-icon"
          aria-label="Delete selected piece"
          onClick={() => onRemovePiece(selectedPieceId)}
        >
          <Trash2 className="size-3.5" aria-hidden="true" />
        </button>
      </div>

      {selectedSectionStatus ? (
        <section className="ite-section">
          <h3 className="ite-section-title">Content rules</h3>
          <SectionStatusLine status={selectedSectionStatus} />
        </section>
      ) : null}

      <SkinPanel
        piece={selectedPiece}
        pieceId={selectedPieceId}
        editor={editor}
        stagedAssetId={stagedAssetId}
        onStageSwap={onStageSwap}
      />

      <TransformPanel
        pieceId={selectedPieceId}
        transform={selectedTransform}
        onChange={onTransformPiece}
        onGestureEnd={onGestureEnd}
      />
    </div>
  )
}

function SectionStatusLine({ status }: { status: SectionStatus }) {
  if (status.role === null) {
    return <p className="ite-status-pill is-empty">No interactive content yet.</p>
  }
  const ok = status.complete
  const label =
    status.role === 'challenge'
      ? `Challenges ${status.count} / 3`
      : `${ARTIFACT_ROLE_LABEL[status.role]}`
  return (
    <div className={cn('ite-status-pill', ok ? 'is-ok' : 'is-warn')}>
      {ok ? <CheckCircle2 className="size-3.5" aria-hidden="true" /> : <AlertTriangle className="size-3.5" aria-hidden="true" />}
      <div className="ite-status-pill-body">
        <span className="ite-status-pill-label">{label}</span>
        {status.issues.length > 0 ? (
          <span className="ite-status-pill-detail">{status.issues[0]}</span>
        ) : (
          <span className="ite-status-pill-detail">Complete.</span>
        )}
      </div>
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
  onGestureEnd,
}: {
  pieceId: number
  transform: PieceTransform
  onChange: (pieceId: number, next: PieceTransform) => void
  onGestureEnd: () => void
}) {
  function update(field: keyof PieceTransform, value: number) {
    if (!Number.isFinite(value)) return
    const clamped =
      field === 'scaleX' || field === 'scaleY'
        ? clampNumber(value, PIECE_SCALE_RANGE.min, PIECE_SCALE_RANGE.max)
        : field === 'rotation'
          ? clampNumber(value, PIECE_ROTATION_RANGE.min, PIECE_ROTATION_RANGE.max)
          : value
    onChange(pieceId, { ...transform, [field]: clamped })
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
          onClick={() => {
            onChange(pieceId, IDENTITY_PIECE_TRANSFORM)
            onGestureEnd()
          }}
        >
          Reset
        </button>
      </div>
      <p className="ite-hint">Drag the frame to move; corners scale, edges stretch one axis (hold Shift to keep aspect); the top grip rotates.</p>
      <div className="ite-field-grid">
        <NumberField label="X" unit="px" value={transform.x} step={1} onCommit={(v) => update('x', v)} onCommitEnd={onGestureEnd} />
        <NumberField label="Y" unit="px" value={transform.y} step={1} onCommit={(v) => update('y', v)} onCommitEnd={onGestureEnd} />
        <NumberField
          label="Scale X"
          unit="x"
          value={transform.scaleX}
          step={0.05}
          min={PIECE_SCALE_RANGE.min}
          max={PIECE_SCALE_RANGE.max}
          onCommit={(v) => update('scaleX', v)}
          onCommitEnd={onGestureEnd}
        />
        <NumberField
          label="Scale Y"
          unit="x"
          value={transform.scaleY}
          step={0.05}
          min={PIECE_SCALE_RANGE.min}
          max={PIECE_SCALE_RANGE.max}
          onCommit={(v) => update('scaleY', v)}
          onCommitEnd={onGestureEnd}
        />
        <NumberField
          label="Rotate"
          unit="deg"
          value={transform.rotation}
          step={1}
          min={PIECE_ROTATION_RANGE.min}
          max={PIECE_ROTATION_RANGE.max}
          onCommit={(v) => update('rotation', v)}
          onCommitEnd={onGestureEnd}
        />
      </div>
    </section>
  )
}

function ArtifactTransformPanel({
  artifact,
  transform,
  onChange,
  onGestureEnd,
}: {
  artifact: ArtifactPlacementDescriptor
  transform: ArtifactTransform
  onChange: (next: ArtifactTransform) => void
  onGestureEnd: () => void
}) {
  function update(field: keyof ArtifactTransform, value: number) {
    if (!Number.isFinite(value)) return
    const next = {
      ...transform,
      [field]:
        field === 'scale'
          ? clampNumber(value, ARTIFACT_SCALE_RANGE.min, ARTIFACT_SCALE_RANGE.max)
          : field === 'rotation'
            ? clampNumber(value, ARTIFACT_ROTATION_RANGE.min, ARTIFACT_ROTATION_RANGE.max)
            : value,
    }
    onChange(next)
  }

  const committed = readArtifactTransform(artifact)
  const canReset = (Object.keys(transform) as (keyof ArtifactTransform)[]).some((key) => transform[key] !== committed[key])

  return (
    <section className="ite-section">
      <div className="ite-section-head">
        <h3 className="ite-section-title">Transform</h3>
        <button
          type="button"
          className="ite-mini-btn"
          disabled={!canReset}
          onClick={() => {
            onChange(committed)
            onGestureEnd()
          }}
        >
          Reset
        </button>
      </div>
      <p className="ite-hint">Drag the frame to move; corners and edges resize the artifact (hold Shift to keep aspect).</p>
      <div className="ite-field-grid">
        <NumberField label="X" unit="px" value={transform.x} step={1} onCommit={(v) => update('x', v)} onCommitEnd={onGestureEnd} />
        <NumberField label="Y" unit="px" value={transform.y} step={1} onCommit={(v) => update('y', v)} onCommitEnd={onGestureEnd} />
        <NumberField label="Width" unit="px" value={transform.width} step={1} min={1} onCommit={(v) => update('width', v)} onCommitEnd={onGestureEnd} />
        <NumberField label="Height" unit="px" value={transform.height} step={1} min={1} onCommit={(v) => update('height', v)} onCommitEnd={onGestureEnd} />
        <NumberField
          label="Scale"
          unit="x"
          value={transform.scale}
          step={0.05}
          min={ARTIFACT_SCALE_RANGE.min}
          max={ARTIFACT_SCALE_RANGE.max}
          onCommit={(v) => update('scale', v)}
          onCommitEnd={onGestureEnd}
        />
        <NumberField
          label="Rotate"
          unit="deg"
          value={transform.rotation}
          step={1}
          min={ARTIFACT_ROTATION_RANGE.min}
          max={ARTIFACT_ROTATION_RANGE.max}
          onCommit={(v) => update('rotation', v)}
          onCommitEnd={onGestureEnd}
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
  onCommitEnd,
}: {
  label: string
  unit?: string
  value: number
  step?: number
  min?: number
  max?: number
  onCommit: (value: number) => void
  onCommitEnd?: () => void
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
        onBlur={() => onCommitEnd?.()}
      />
    </label>
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
