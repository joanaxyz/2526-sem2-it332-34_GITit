import { useMemo, useState } from 'react'
import { Copy, Eye, Layers, Maximize2, Minus, Plus, Share2, UploadCloud } from 'lucide-react'

import { EditorCanvas } from '@/features/tower-designs/components/EditorCanvas'
import { PiecePalette } from '@/features/tower-designs/components/PiecePalette'
import { PieceInspector } from '@/features/tower-designs/components/PieceInspector'
import { UploadAssetDialog } from '@/features/tower-designs/components/UploadAssetDialog'
import { useDesignEditor } from '@/features/tower-designs/hooks/useDesignEditor'
import { towerDescriptorFor, pieceHasWalkRail } from '@/features/tower-map/components/towerPieceData'
import { SectionEditor } from '@/features/tower-map/editor/SectionEditor'
import { useZoomPan } from '@/features/tower-map/editor/useZoomPan'
import { ApiError } from '@/shared/api/apiError'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

/** Inline editable tower name, saved on blur/Enter (never to an empty value). */
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

/**
 * The tower editor, rendered INSIDE the tower page over the living sky. The page
 * keeps only its background + clock in edit mode; everything else (docks,
 * companion, picker) is hidden by TowerMapPage. Exiting returns to the full
 * preview of the tower with no route change.
 */
export function InTowerEditor({ designId, onExit }: { designId: number; onExit: () => void }) {
  const editor = useDesignEditor(designId)
  const zoom = useZoomPan()
  const [selectedPieceId, setSelectedPieceId] = useState<number | null>(null)
  const [sectionPieceId, setSectionPieceId] = useState<number | null>(null)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [copied, setCopied] = useState(false)

  const shared = editor.share.data
  const shareUrl = shared?.share_path ? `${window.location.origin}${shared.share_path}` : null
  const shareError = publishErrorMessage(editor.share.error)

  const walkRailWarnings = useMemo(() => {
    if (!editor.overview) return []
    return editor.overview.tower_layout.pieces
      .filter((p) => p.pieceType === 'landing')
      .filter((p) => !pieceHasWalkRail(editor.pieceDescriptorBySlug[p.assetSlug]))
  }, [editor.overview, editor.pieceDescriptorBySlug])

  const sectionPiece = useMemo(() => {
    if (sectionPieceId === null || !editor.overview) return null
    return (
      editor.overview.tower_layout.pieces.find(
        (p) => editor.pieceIdFromInstance(p.instanceId) === sectionPieceId,
      ) ?? null
    )
  }, [sectionPieceId, editor.overview, editor.pieceIdFromInstance])

  function copyShareUrl() {
    if (!shareUrl) return
    void navigator.clipboard?.writeText(shareUrl).then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    })
  }

  if (editor.isLoading) return <LoadingState label="Opening the editor" variant="page" />
  if (editor.isError || !editor.overview) {
    return <ErrorState title="Could not open this tower" description={(editor.error as Error)?.message ?? ''} />
  }

  const overview = editor.overview
  const isFork = overview.design.origin === 'official_fork'
  const publishError = publishErrorMessage(editor.publish.error)

  return (
    <div className="in-tower-editor">
      <header className="ite-bar">
        <div className="ite-bar-left">
          <Button variant="outline" size="sm" onClick={onExit}>
            <Eye className="size-4" aria-hidden="true" />
            Preview
          </Button>
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

        <div className="ite-bar-tools" role="group" aria-label="Zoom">
          <button type="button" className="editor-icon-btn" onClick={zoom.zoomOut} aria-label="Zoom out">
            <Minus className="size-4" aria-hidden="true" />
          </button>
          <span className="ite-zoom-readout">{Math.round(zoom.scale * 100)}%</span>
          <button type="button" className="editor-icon-btn" onClick={zoom.zoomIn} aria-label="Zoom in">
            <Plus className="size-4" aria-hidden="true" />
          </button>
          <button type="button" className="editor-icon-btn" onClick={zoom.reset} aria-label="Reset view">
            <Maximize2 className="size-4" aria-hidden="true" />
          </button>
        </div>

        <div className="ite-bar-right">
          <Button variant="outline" size="sm" disabled={editor.addStorey.isPending} onClick={() => editor.addStorey.mutate()}>
            <Layers className="size-4" aria-hidden="true" />
            Add storey
          </Button>
          {isFork ? (
            <span className="editor-fork-note">Private edits to the official tower — only you see these.</span>
          ) : (
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
          {walkRailWarnings.length} landing{walkRailWarnings.length > 1 ? 's' : ''} can&apos;t be walked by Blue — swap in
          a landing marked with a footprint before publishing.
        </p>
      ) : null}
      {publishError ? <p className="editor-warning is-error">{publishError}</p> : null}

      {uploadOpen ? <UploadAssetDialog onClose={() => setUploadOpen(false)} /> : null}

      <div className="ite-grid">
        <PiecePalette
          pieces={editor.pieceDescriptors}
          artifacts={editor.artifactDescriptors}
          onUploadClick={() => setUploadOpen(true)}
        />

        <div className="ite-canvas-viewport" onWheel={zoom.onWheel} onPointerDown={zoom.onPanStart}>
          <p className="ite-canvas-hint">Click a section to select · double-click to edit it · scroll to zoom · drag the sky to pan</p>
          <div className="ite-canvas-content" style={zoom.style}>
            <EditorCanvas
              overview={overview}
              pieceDescriptorBySlug={editor.pieceDescriptorBySlug}
              artifactDescriptorBySlug={editor.artifactDescriptorBySlug}
              selectedPieceId={selectedPieceId}
              onSelectPiece={setSelectedPieceId}
              onSwapAsset={(pieceId, assetId) => editor.swapAsset.mutate({ pieceId, assetId })}
              onPlaceArtifact={(pieceId, assetId, x, y) =>
                editor.placeArtifact.mutate({ target_piece_instance_id: pieceId, artifact_asset_id: assetId, x, y })
              }
              onMoveArtifact={(placementId, x, y) => editor.updateArtifact.mutate({ placementId, x, y })}
              onOpenSection={setSectionPieceId}
            />
          </div>
        </div>

        <PieceInspector overview={overview} selectedPieceId={selectedPieceId} editor={editor} />
      </div>

      {sectionPiece ? (
        <SectionEditor
          overview={overview}
          piece={sectionPiece}
          descriptor={towerDescriptorFor(sectionPiece, editor.pieceDescriptorBySlug)}
          artifactDescriptors={editor.artifactDescriptors}
          artifactDescriptorBySlug={editor.artifactDescriptorBySlug}
          onPlaceArtifact={(pieceId, assetId, x, y) =>
            editor.placeArtifact.mutate({ target_piece_instance_id: pieceId, artifact_asset_id: assetId, x, y })
          }
          onMoveArtifact={(placementId, x, y) => editor.updateArtifact.mutate({ placementId, x, y })}
          onDeleteArtifact={(placementId) => editor.deleteArtifact.mutate(placementId)}
          onClose={() => setSectionPieceId(null)}
        />
      ) : null}
    </div>
  )
}
