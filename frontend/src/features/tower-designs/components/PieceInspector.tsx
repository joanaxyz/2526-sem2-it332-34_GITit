import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Check, Plus, Trash2 } from 'lucide-react'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import { BINDABLE_KIND, PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import type { useDesignEditor } from '@/features/tower-designs/hooks/useDesignEditor'
import type { ArtifactPlacementDescriptor, TowerDesignOverview } from '@/features/tower-designs/types'
import { backendUrl } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import type {
  TowerLayoutPieceDescriptor,
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

type Editor = ReturnType<typeof useDesignEditor>

function descriptorPieceType(descriptor: TowerPieceAssetDescriptor): TowerPieceType | undefined {
  return descriptor.piece_type ?? descriptor.tower_piece?.piece_type
}

function pieceThumb(descriptor: TowerPieceAssetDescriptor): string | null {
  const sprite = descriptor.sprites.default ?? Object.values(descriptor.sprites)[0]
  return sprite?.url ? backendUrl(sprite.url) : null
}

export function PieceInspector({
  overview,
  selectedPieceId,
  editor,
}: {
  overview: TowerDesignOverview
  selectedPieceId: number | null
  editor: Editor
}) {
  const piece = selectedPieceId
    ? overview.tower_layout.pieces.find((p) => editor.pieceIdFromInstance(p.instanceId) === selectedPieceId) ?? null
    : null

  if (!piece || selectedPieceId === null) {
    return (
      <aside className="editor-inspector" aria-label="Piece inspector">
        <p className="editor-inspector-empty">Select a piece in the tower to bind content or place artifacts.</p>
      </aside>
    )
  }

  const bindableKind = BINDABLE_KIND[piece.pieceType as TowerPieceType]
  const artifacts = overview.artifacts.filter((a) => a.targetInstanceId === piece.instanceId)

  return (
    <aside className="editor-inspector" aria-label="Piece inspector">
      <h2 className="editor-rail-title">{PIECE_TYPE_LABEL[piece.pieceType as TowerPieceType]}</h2>

      <SkinPanel piece={piece} pieceId={selectedPieceId} editor={editor} />

      {bindableKind ? (
        <BindingPanel
          kind={bindableKind}
          piece={piece}
          pieceId={selectedPieceId}
          editor={editor}
        />
      ) : null}

      <ArtifactList artifacts={artifacts} editor={editor} />
    </aside>
  )
}

/**
 * Restyle the selected piece: click any same-type sprite (official Arcane Spire
 * kit + the player's own uploads) to apply it. This is the primary way to change
 * a structural piece's look — reliable click-to-apply, no drag needed. (Artifacts
 * are still dragged from the palette onto a section.)
 */
function SkinPanel({
  piece,
  pieceId,
  editor,
}: {
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  editor: Editor
}) {
  const skins = editor.pieceDescriptors.filter((d) => descriptorPieceType(d) === piece.pieceType)

  return (
    <section className="editor-panel">
      <h3 className="editor-panel-title">Skin</h3>
      {skins.length === 0 ? (
        <p className="editor-inspector-empty">No sprites available for this piece yet.</p>
      ) : (
        <div className="editor-skin-grid">
          {skins.map((descriptor) => {
            const isActive = descriptor.slug === piece.assetSlug
            const thumb = pieceThumb(descriptor)
            return (
              <button
                key={descriptor.slug}
                type="button"
                className={cn('editor-skin-cell', `is-${descriptor.source ?? 'official'}`, isActive && 'is-active')}
                title={descriptor.label}
                aria-label={descriptor.label}
                aria-pressed={isActive}
                disabled={editor.swapAsset.isPending}
                onClick={() => {
                  if (!isActive) editor.swapAsset.mutate({ pieceId, assetId: descriptor.id })
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
      )}
    </section>
  )
}

function BindingPanel({
  kind,
  piece,
  pieceId,
  editor,
}: {
  kind: 'adventure' | 'challenge' | 'tome'
  piece: TowerLayoutPieceDescriptor
  pieceId: number
  editor: Editor
}) {
  const contentQuery = useQuery({
    queryKey: queryKeys.authoringContent(kind),
    queryFn: () => authoringApi.list(kind),
  })
  const boundId = piece.contentBinding ? Number(piece.contentBinding.id) : null
  const options = (contentQuery.data?.results ?? []).filter(
    (c) => c.status === 'published' || c.status === 'testable',
  )

  return (
    <section className="editor-panel">
      <h3 className="editor-panel-title">Bound content</h3>
      {options.length === 0 ? (
        <p className="editor-inspector-empty">
          No {kind}s ready to bind yet.
        </p>
      ) : (
        <ul className="editor-bind-list">
          {options.map((content) => {
            const isBound = content.id === boundId
            return (
              <li key={content.id}>
                <button
                  type="button"
                  className={cn('editor-bind-row', isBound && 'is-bound')}
                  onClick={() =>
                    editor.bind.mutate({ piece_instance_id: pieceId, content_definition_id: content.id })
                  }
                >
                  <span className="editor-bind-title">{content.title}</span>
                  <span className="editor-bind-status">{content.status}</span>
                  {isBound ? <Check className="size-4 text-[color:hsl(var(--primary))]" aria-hidden="true" /> : null}
                </button>
              </li>
            )
          })}
        </ul>
      )}

      <Link className="editor-author-link" to={`/authoring/new/${kind}`}>
        <Plus className="size-3.5" aria-hidden="true" />
        Author a new {kind}
      </Link>
    </section>
  )
}

function ArtifactList({ artifacts, editor }: { artifacts: ArtifactPlacementDescriptor[]; editor: Editor }) {
  return (
    <section className="editor-panel">
      <h3 className="editor-panel-title">Artifacts on this piece</h3>
      {artifacts.length === 0 ? (
        <p className="editor-inspector-empty">Drag an artifact from the palette onto this piece.</p>
      ) : (
        <ul className="editor-artifact-list">
          {artifacts.map((artifact) => (
            <li key={artifact.id} className="editor-artifact-row">
              <span className="editor-artifact-slug">{artifact.assetSlug}</span>
              <button
                type="button"
                className="editor-icon-btn"
                aria-label="Remove artifact"
                onClick={() => editor.deleteArtifact.mutate(artifact.id)}
              >
                <Trash2 className="size-4" aria-hidden="true" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
