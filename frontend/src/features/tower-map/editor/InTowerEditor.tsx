import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
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
import { validateDesign, type DesignIssue } from '@/features/tower-designs/editorValidation'
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
    | { detail?: string; validation_errors?: { message: string }[];[key: string]: unknown }
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
  const issues = useMemo<DesignIssue[]>(
    () => (editor.overview ? validateDesign(editor.overview) : []),
    [editor.overview],
  )

  const flashToast = useCallback((message: string, kind: 'error' | 'info' = 'error') => {
    setToast({ kind, message })
    window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 3600)
  }, [])

  const clearSelection = useCallback(() => {
    setSelectedPieceId(null)
    setSelectedArtifactId(null)
    setPlacementDraft(null)
  }, [])

  const removeArtifact = useCallback(
    (placementId: number | string) => {
      const currentOverview = editor.overview
      if (!currentOverview) return
      // The official tower's interactive doors are the curriculum's - on the fork
      // you may move or re-skin them, but removing one would hide a learning step,
      // so deletion is blocked (decorative artifacts you added stay removable).
      const target = currentOverview.artifacts.find((item) => item.id === placementId) ?? null
      if (currentOverview.design.origin === 'official_fork' && target && target.role !== 'normal') {
        flashToast('Interactive doors on the official tower can be moved or re-skinned, but not removed.', 'info')
        return
      }
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
    },
    [editor.deleteArtifact, editor.overview, flashToast, staged],
  )

  const deleteSelection = useCallback(() => {
    const currentOverview = editor.overview

    if (selectedArtifactId !== null) {
      removeArtifact(selectedArtifactId)
      setSelectedPieceId(null)
      setPlacementDraft(null)
      return
    }

    if (selectedPieceId === null || !currentOverview) return

    const deletedPiece = currentOverview.tower_layout.pieces.find(
      (piece) => pieceIdFromInstance(piece.instanceId) === selectedPieceId,
    )

    editor.deletePiece.mutate(selectedPieceId, {
      onError: (error) => flashToast(apiErrorMessage(error) ?? 'Could not delete piece.'),
    })

    staged.commit((state) => {
      let changed = false
      const pendingSwaps = new Map(state.pendingSwaps)
      const pieceTransforms = new Map(state.pieceTransforms)
      const artifactEdits = new Map(state.artifactEdits)

      if (pendingSwaps.delete(selectedPieceId)) changed = true
      if (pieceTransforms.delete(selectedPieceId)) changed = true

      if (deletedPiece) {
        for (const artifact of currentOverview.artifacts) {
          if (artifact.targetInstanceId === deletedPiece.instanceId && artifactEdits.delete(artifact.id)) {
            changed = true
          }
        }
      }

      if (!changed) return state
      return { ...state, pendingSwaps, pieceTransforms, artifactEdits }
    })

    staged.endGesture()
    clearSelection()
  }, [clearSelection, editor.deletePiece, editor.overview, flashToast, removeArtifact, selectedArtifactId, selectedPieceId, staged])

  // Editor hotkeys. Defer to native text editing while a form control is focused.
  const { undo: undoEdit, redo: redoEdit } = staged
  useEffect(() => {
    function isTypingTarget(target: EventTarget | null) {
      const element = target instanceof HTMLElement ? target : null
      if (!element) return false
      return Boolean(element.closest('input, textarea, select, [contenteditable="true"]'))
    }

    function onKey(event: KeyboardEvent) {
      if (uploadOpen || isTypingTarget(event.target)) return

      if (event.key === 'Escape') {
        if (selectedPieceId !== null || selectedArtifactId !== null || placementDraft) {
          event.preventDefault()
          clearSelection()
        }
        setShowIssues(false)
        return
      }

      if ((event.key === 'Delete' || event.key === 'Backspace') && !event.ctrlKey && !event.metaKey && !event.altKey) {
        if (event.repeat) return
        if (selectedPieceId !== null || selectedArtifactId !== null) {
          event.preventDefault()
          deleteSelection()
        }
        return
      }

      if (!(event.ctrlKey || event.metaKey)) return

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
  }, [
    clearSelection,
    deleteSelection,
    placementDraft,
    redoEdit,
    selectedArtifactId,
    selectedPieceId,
    undoEdit,
    uploadOpen,
  ])

  useEffect(() => () => window.clearTimeout(toastTimer.current), [])

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

  function moveArtifact(placementId: number | string, targetInstanceId: string, x: number, y: number) {
    const base = overview.artifacts.find((a) => a.id === placementId)
    const targetPieceId = pieceIdFromInstance(targetInstanceId)
    if (selectedArtifactId === placementId && targetPieceId !== null) {
      setSelectedPieceId(targetPieceId)
    }
    staged.commit((state) => {
      const map = new Map(state.artifactEdits)
      const next = { ...(map.get(placementId) ?? {}), x, y }
      if (!base || targetInstanceId !== base.targetInstanceId) next.targetInstanceId = targetInstanceId
      else delete next.targetInstanceId
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
        zIndex: transform.zIndex,
      }
      if (editMatchesBase(next, artifact)) map.delete(artifact.id)
      else map.set(artifact.id, next)
      return { ...state, artifactEdits: map }
    }, `artifact:${artifact.id}`)
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
        const { targetInstanceId, zIndex, ...rest } = edit
        const input: typeof rest & { target_piece_instance_id?: number; z_index?: number } = { ...rest }
        if (targetInstanceId) {
          const targetPieceId = pieceIdFromInstance(targetInstanceId)
          if (targetPieceId !== null) input.target_piece_instance_id = targetPieceId
        }
        if (zIndex !== undefined) input.z_index = zIndex
        jobs.push(editor.updateArtifact.mutateAsync({ placementId, ...input }))
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

  function focusIssue(issue: DesignIssue) {
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
  return (
    <div className="ite-shell">
      {uploadOpen ? <UploadAssetDialog onClose={() => setUploadOpen(false)} /> : null}

      <EditorCommandBar
        overview={overview}
        isFork={isFork}
        onExit={onExit}
        renamePending={editor.rename.isPending}
        onRename={(next) => editor.rename.mutate(next)}
        pieceCount={pieceCount}
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

      <div className="ite-body">
        <aside className="ite-rail ite-rail--library" aria-label="Asset library">
          <StoragePanel
            overview={overview}
            editor={editor}
            placementDraft={placementDraft}
            onUploadClick={() => setUploadOpen(true)}
            onPlacementDraft={setPlacementDraft}
          />
        </aside>

        <div className="ite-canvas-col">
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
            onPointerDown={(event) => {
              const target = event.target

              const clickedSelectable =
                target instanceof Element &&
                target.closest('.editor-piece, .editor-artifact, .ed-tf, .tower-artifact')

              if (!clickedSelectable) {
                clearSelection()
              }

              zoom.onPanStart(event)
            }}
          >
            {/* The zoom/pan transform rides this inner layer, NOT the viewport
                above it. Keeping the clip frame (overflow:hidden) untransformed
                means panning can reveal a tall tower's clipped ends, and the
                scaled canvas never overflows into the side rails. */}
            <div className="ite-canvas-content" style={zoom.style}>
            <EditorStorey
              overview={overview}
              pieceDescriptorBySlug={editor.pieceDescriptorBySlug}
              pieceDescriptorById={pieceDescriptorById}
              artifactDescriptorBySlug={editor.artifactDescriptorBySlug}
              selectedPieceId={selectedPieceId}
              selectedArtifactId={selectedArtifactId}
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
              onPlaceArtifact={(pieceId, assetId, x, y) => {
                const size = artifactSize(assetId)
                editor.placeArtifact.mutate(
                  {
                    target_piece_instance_id: pieceId,
                    artifact_asset_id: assetId,
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
            />
            </div>
          </section>
        </div>

        <aside className="ite-rail ite-rail--inspector" aria-label="Inspector">
          <PropertiesPanel
            overview={overview}
            editor={editor}
            selectedPieceId={selectedPieceId}
            selectedPiece={selectedPiece}
            selectedArtifact={selectedArtifact}
            selectedTransform={selectedTransform}
            selectedArtifactTransform={selectedArtifactTransform}
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
          />
        </aside>
      </div>

      {toast ? (
        <div className={cn('ite-toast', toast.kind === 'error' && 'is-error')} role="status" aria-live="polite">
          <AlertTriangle className="size-4" aria-hidden="true" />
          <span>{toast.message}</span>
        </div>
      ) : null}

      {staged.dirtyCount > 0 ? (
        <footer className="ite-footer" role="region" aria-label="Unsaved changes">
          <span className="ite-apply-dot" aria-hidden="true" />
          <span className="ite-apply-bar-label">
            {staged.dirtyCount} unsaved change{staged.dirtyCount > 1 ? 's' : ''}
          </span>
          <div className="ite-footer-actions">
            <Button size="sm" variant="ghost" disabled={applying} onClick={() => staged.reset()}>
              Discard
            </Button>
            <Button size="sm" disabled={applying} onClick={applyChanges}>
              {applying ? 'Applying…' : 'Apply changes'}
            </Button>
          </div>
        </footer>
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
  pieceCount,
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
  pieceCount: number
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
          Spire + repeating storey · {pieceCount} piece{pieceCount === 1 ? '' : 's'}
        </p>
      </div>

      <div className="ite-cmd-template" aria-label="Tower template">
        <span className="ite-template-label">Tower Template</span>
        <span className="ite-template-copy">Spire + Repeating Storey</span>
      </div>

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
                <span className="ite-issue-storey">Template</span>
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
  onUploadClick,
  onPlacementDraft,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  placementDraft: PlacementDraft
  onUploadClick: () => void
  onPlacementDraft: (draft: PlacementDraft) => void
}) {
  const [tag, setTag] = useState<string>('all')

  // Tags are a property of every asset, not just artifacts, so the filter spans
  // the whole library (pieces and artifacts alike) rather than sitting under one
  // shelf as if it were an artifact-only field.
  const allTags = useMemo(() => {
    const set = new Set<string>()
    for (const descriptor of editor.pieceDescriptors) {
      for (const value of descriptor.tags ?? []) set.add(value)
    }
    for (const descriptor of editor.artifactDescriptors) {
      for (const value of descriptor.tags ?? []) set.add(value)
    }
    return [...set].sort()
  }, [editor.pieceDescriptors, editor.artifactDescriptors])

  const byTag = useCallback(
    <T extends { tags?: string[] }>(descriptors: T[]): T[] =>
      tag === 'all' ? descriptors : descriptors.filter((d) => (d.tags ?? []).includes(tag)),
    [tag],
  )
  const filtering = tag !== 'all'

  const spires = byTag(editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === 'crown'))
  const sections = byTag(editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === 'section'))
  const landings = byTag(editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === 'landing'))
  const artifacts = byTag(editor.artifactDescriptors)
  const noneMatch = filtering && !spires.length && !sections.length && !landings.length && !artifacts.length

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

      {allTags.length > 0 ? (
        <div className="ite-library-filter">
          <span className="ite-field-label">Tag</span>
          <select
            className="ite-tag-filter"
            value={tag}
            onChange={(event) => setTag(event.target.value)}
            aria-label="Filter library by tag"
          >
            <option value="all">All tags</option>
            {allTags.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      <StoragePieceShelf title="Spire" descriptors={spires} hideWhenEmpty={filtering} />
      <StoragePieceShelf title="Sections" descriptors={sections} hideWhenEmpty={filtering} />
      <StoragePieceShelf title="Landings" descriptors={landings} hideWhenEmpty={filtering} />

      {filtering && !artifacts.length ? null : (
        <section className="ite-section">
          <div className="ite-section-head">
            <h3 className="ite-section-title">Artifacts</h3>
            <span className="ite-rule-pill">{artifacts.length}</span>
          </div>
          <p className="ite-hint">Drop any artifact onto the tower. Select it afterwards to make it interactive.</p>
          <StorageArtifactGrid
            descriptors={artifacts}
            active={placementDraft}
            payloadFor={(descriptor) => ({
              source: 'asset-artifact',
              assetId: descriptor.id,
              slug: descriptor.slug,
            })}
            onPlacementDraft={onPlacementDraft}
          />
        </section>
      )}

      {noneMatch ? <p className="ite-empty ite-empty--inline">No assets match this tag.</p> : null}

      {placementDraft ? <p className="editor-palette-active">Drag to a tower piece, or click the destination piece.</p> : null}
    </div>
  )
}

function StoragePieceShelf({
  title,
  descriptors,
  hideWhenEmpty = false,
}: {
  title: string
  descriptors: TowerPieceAssetDescriptor[]
  hideWhenEmpty?: boolean
}) {
  if (hideWhenEmpty && descriptors.length === 0) return null
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
          active.assetId === payload.assetId
        return (
          <button
            type="button"
            key={descriptor.slug}
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
  stagedAssetId,
  onStageSwap,
  onTransformPiece,
  onTransformArtifact,
  onGestureEnd,
  onRemovePiece,
  onRemoveArtifact,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  selectedPieceId: number | null
  selectedPiece: TowerLayoutPieceDescriptor | null
  selectedArtifact: ArtifactPlacementDescriptor | null
  selectedTransform: PieceTransform
  selectedArtifactTransform: ArtifactTransform | null
  stagedAssetId: number | null
  onStageSwap: (pieceId: number, assetId: number) => void
  onTransformPiece: (pieceId: number, next: PieceTransform) => void
  onTransformArtifact: (artifact: ArtifactPlacementDescriptor, next: ArtifactTransform) => void
  onGestureEnd: () => void
  onRemovePiece: (pieceId: number) => void
  onRemoveArtifact: (placementId: number | string) => void
}) {
  // On the official tower's private fork the interactive doors belong to the
  // curriculum: you can reposition and re-skin them, but not author/rebind their
  // content or delete them (that would hide a learning step).
  const isFork = overview.design.origin === 'official_fork'

  if (selectedArtifact && selectedArtifactTransform) {
    const roleLabel =
      selectedArtifact.role === 'normal' ? 'Artifact' : ARTIFACT_ROLE_LABEL[selectedArtifact.role]
    const lockedInteractive = isFork && selectedArtifact.role !== 'normal'
    return (
      <div className="ite-inspector" aria-label="Artifact properties">
        <div className="ite-section ite-section--head">
          <div>
            <p className="ite-eyebrow">Artifact</p>
            <h2 className="ite-section-heading">{roleLabel}</h2>
          </div>
          {lockedInteractive ? null : (
            <button
              type="button"
              className="editor-danger-icon"
              aria-label="Remove artifact"
              onClick={() => onRemoveArtifact(selectedArtifact.id)}
            >
              <Trash2 className="size-3.5" aria-hidden="true" />
            </button>
          )}
        </div>
        <ArtifactTransformPanel
          artifact={selectedArtifact}
          transform={selectedArtifactTransform}
          onChange={(next) => onTransformArtifact(selectedArtifact, next)}
          onGestureEnd={onGestureEnd}
        />
        {isFork ? null : (
          <ArtifactInteractivePanel overview={overview} editor={editor} artifact={selectedArtifact} />
        )}
      </div>
    )
  }

  if (!selectedPiece || selectedPieceId === null) {
    return (
      <div className="ite-inspector ite-inspector--empty" aria-label="Inspector">
        <p className="ite-empty">Select a tower piece to edit its properties, or pick an artifact to transform it.</p>
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

// Promote/demote a selected artifact. Every artifact starts `normal`; this is
// where the author optionally binds it to a quest / challenge / tome (or reverts
// it). Role + content changes go straight to the server via updateArtifact (the
// same immediate path as place/delete), independent of the staged transform edits.
function ArtifactInteractivePanel({
  overview,
  editor,
  artifact,
}: {
  overview: TowerDesignOverview
  editor: ReturnType<typeof useDesignEditor>
  artifact: ArtifactPlacementDescriptor
}) {
  const isInteractive = artifact.role !== 'normal'
  const [role, setRole] = useState<TowerArtifactRole>(isInteractive ? artifact.role : 'adventure')
  const [contentId, setContentId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const contentQuery = useQuery({
    queryKey: queryKeys.authoringContent(role as ContentKind),
    queryFn: () => authoringApi.list(role as ContentKind),
    enabled: !isInteractive,
  })
  const options = (contentQuery.data?.results ?? []).filter(
    (content) => content.status === 'published' || content.status === 'testable',
  )
  // Content is optional: an artifact can be interactive with nothing bound yet
  // (the author wires it up later). `null` means "no content yet".
  const chosen = contentId
  const pending = editor.updateArtifact.isPending

  // Promote/demote PATCHes a persisted placement; brand-new placements always
  // have a numeric id by the time they can be selected.
  if (typeof artifact.id !== 'number') return null
  const placementId = artifact.id

  function fail(err: unknown) {
    setError(apiErrorMessage(err) ?? 'Could not update artifact.')
  }

  if (isInteractive) {
    const content = contentForArtifact(overview, artifact)
    const authorHref = content ? `/authoring/${content.id}` : `/authoring/new/${artifact.role}`
    return (
      <section className="ite-section">
        <h3 className="ite-section-title">Interactive content</h3>
        <Link className="ite-quest-action" to={authorHref}>
          <PencilLine className="size-3.5" aria-hidden="true" />
          {content ? `Author ${content.title}` : 'Author content'}
        </Link>
        <button
          type="button"
          className="ite-mini-btn"
          disabled={pending}
          onClick={() =>
            editor.updateArtifact.mutate(
              { placementId, role: 'normal', content_definition_id: null },
              { onError: fail },
            )
          }
        >
          Make normal
        </button>
        {error ? <p className="ite-status-msg is-error">{error}</p> : null}
      </section>
    )
  }

  return (
    <section className="ite-section">
      <h3 className="ite-section-title">Make interactive</h3>
      <p className="ite-hint">Pick what this artifact opens. You can bind content now, or author it later.</p>
      <div className="ite-field-grid">
        <label className="ite-field">
          <span className="ite-field-label">Kind</span>
          <select
            className="ite-field-input"
            value={role}
            onChange={(event) => {
              setRole(event.target.value as TowerArtifactRole)
              setContentId(null)
            }}
          >
            {INTERACTABLE_ROLES.map((value) => (
              <option key={value} value={value}>
                {ARTIFACT_ROLE_LABEL[value]}
              </option>
            ))}
          </select>
        </label>
        <label className="ite-field">
          <span className="ite-field-label">Content</span>
          <select
            className="ite-field-input"
            value={chosen ?? ''}
            onChange={(event) => setContentId(event.target.value ? Number(event.target.value) : null)}
          >
            <option value="">No content yet</option>
            {options.map((content) => (
              <option key={content.id} value={content.id}>
                {content.title}
              </option>
            ))}
          </select>
        </label>
      </div>
      <Button
        size="sm"
        disabled={pending}
        onClick={() =>
          editor.updateArtifact.mutate({ placementId, role, content_definition_id: chosen }, { onError: fail })
        }
      >
        {pending ? 'Saving…' : 'Make interactive'}
      </Button>
      <p className="ite-hint">Bind and publish content before you share the tower.</p>
      {error ? <p className="ite-status-msg is-error">{error}</p> : null}
    </section>
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
        <NumberField
          label="Z index"
          value={transform.zIndex}
          step={1}
          onCommit={(v) => update('zIndex', v)}
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
        <NumberField
          label="Z index"
          value={transform.zIndex}
          step={1}
          onCommit={(v) => update('zIndex', v)}
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
  if (edit.targetInstanceId !== undefined && edit.targetInstanceId !== base.targetInstanceId) return false
  return (Object.keys(edit) as (keyof ArtifactEdit)[])
    .filter((key) => key !== 'targetInstanceId')
    .every((key) => edit[key] === base[key])
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
