import { useMemo, useState } from 'react'
import { Footprints, Upload } from 'lucide-react'

import { PieceFilterDropdown } from '@/features/tower-designs/components/PieceFilterDropdown'
import { PALETTE_GROUPS, PIECE_TYPE_LABEL } from '@/features/tower-designs/editorUtils'
import { pieceHasWalkRail } from '@/features/tower-map/components/towerPieceData'
import { backendUrl } from '@/shared/api/httpClient'
import type { AssetSource } from '@/shared/assets/types'
import type {
  TowerArtifactAssetDescriptor,
  TowerPieceAssetDescriptor,
  TowerPieceType,
} from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

export type PaletteDragPayload =
  | { source: 'palette-piece'; assetId: number; slug: string; pieceType: string }
  | { source: 'palette-artifact'; assetId: number; slug: string }

type PaletteGroup = TowerPieceType | 'artifact'

type PaletteItem = {
  id: number
  slug: string
  label: string
  thumb: string | null
  group: PaletteGroup
  assetSource: AssetSource
  tags: string[]
  walkable: boolean
  payload: PaletteDragPayload
}

const SOURCE_LABEL: Record<AssetSource, string> = {
  official: 'Official',
  owned: 'Yours',
  purchased: 'Purchased',
}
const SOURCE_ORDER: AssetSource[] = ['official', 'owned', 'purchased']

function setDrag(event: React.DragEvent, payload: PaletteDragPayload) {
  event.dataTransfer.setData('application/json', JSON.stringify(payload))
  event.dataTransfer.effectAllowed = 'copy'
}

function thumbUrl(descriptor: { sprites: Record<string, { url: string }> }) {
  const sprite = descriptor.sprites.default ?? Object.values(descriptor.sprites)[0]
  return sprite?.url ? backendUrl(sprite.url) : null
}

function buildItems(
  pieces: TowerPieceAssetDescriptor[],
  artifacts: TowerArtifactAssetDescriptor[],
): PaletteItem[] {
  const items: PaletteItem[] = []
  for (const descriptor of pieces) {
    const type = (descriptor.piece_type ?? descriptor.tower_piece?.piece_type) as TowerPieceType | undefined
    if (!type) continue
    items.push({
      id: descriptor.id,
      slug: descriptor.slug,
      label: descriptor.label,
      thumb: thumbUrl(descriptor),
      group: type,
      assetSource: descriptor.source ?? 'official',
      tags: descriptor.tags ?? [],
      walkable: type === 'landing' && pieceHasWalkRail(descriptor),
      payload: { source: 'palette-piece', assetId: descriptor.id, slug: descriptor.slug, pieceType: type },
    })
  }
  for (const descriptor of artifacts) {
    items.push({
      id: descriptor.id,
      slug: descriptor.slug,
      label: descriptor.label,
      thumb: thumbUrl(descriptor),
      group: 'artifact',
      assetSource: descriptor.source ?? 'official',
      tags: descriptor.tags ?? [],
      walkable: false,
      payload: { source: 'palette-artifact', assetId: descriptor.id, slug: descriptor.slug },
    })
  }
  return items
}

function groupLabel(group: PaletteGroup): string {
  return group === 'artifact' ? 'Artifacts' : PIECE_TYPE_LABEL[group]
}

export function PiecePalette({
  pieces,
  artifacts,
  onUploadClick,
}: {
  pieces: TowerPieceAssetDescriptor[]
  artifacts: TowerArtifactAssetDescriptor[]
  onUploadClick?: () => void
}) {
  const items = useMemo(() => buildItems(pieces, artifacts), [pieces, artifacts])

  const groups = useMemo<PaletteGroup[]>(() => {
    const present = new Set(items.map((item) => item.group))
    const ordered: PaletteGroup[] = [...PALETTE_GROUPS, 'artifact']
    return ordered.filter((group) => present.has(group))
  }, [items])

  const sources = useMemo<AssetSource[]>(() => {
    const present = new Set(items.map((item) => item.assetSource))
    return SOURCE_ORDER.filter((source) => present.has(source))
  }, [items])

  const allTags = useMemo<string[]>(() => {
    const set = new Set<string>()
    for (const item of items) item.tags.forEach((tag) => set.add(tag))
    return [...set].sort()
  }, [items])

  const [group, setGroup] = useState<PaletteGroup | 'all'>('all')
  const [source, setSource] = useState<AssetSource | 'all'>('all')
  const [tags, setTags] = useState<Set<string>>(new Set())
  const [query, setQuery] = useState('')
  const [activeLabel, setActiveLabel] = useState<string | null>(null)

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase()
    return items.filter((item) => {
      if (group !== 'all' && item.group !== group) return false
      if (source !== 'all' && item.assetSource !== source) return false
      if (tags.size && !item.tags.some((tag) => tags.has(tag))) return false
      if (
        needle &&
        !item.label.toLowerCase().includes(needle) &&
        !item.tags.some((tag) => tag.toLowerCase().includes(needle))
      ) {
        return false
      }
      return true
    })
  }, [items, group, source, tags, query])

  function toggleTag(tag: string) {
    setTags((prev) => {
      const next = new Set(prev)
      if (next.has(tag)) next.delete(tag)
      else next.add(tag)
      return next
    })
  }

  return (
    <aside className="editor-palette" aria-label="Tower piece palette">
      <header className="editor-palette-head">
        <h2 className="editor-rail-title">Pieces</h2>
        {/* Single dynamic label: reflects the hovered/focused piece, replacing
            per-row labels so the grid stays compact. */}
        <p className="editor-palette-active" aria-live="polite">
          {activeLabel ?? 'Hover a piece to see its name — drag it onto a matching slot.'}
        </p>
      </header>

      <div className="editor-palette-filters">
        <div className="editor-filter-row" role="group" aria-label="Filter by type">
          <FilterChip active={group === 'all'} onClick={() => setGroup('all')}>
            All
          </FilterChip>
          {groups.map((value) => (
            <FilterChip key={value} active={group === value} onClick={() => setGroup(value)}>
              {groupLabel(value)}
            </FilterChip>
          ))}
        </div>

        {sources.length > 1 ? (
          <div className="editor-filter-row" role="group" aria-label="Filter by source">
            <FilterChip subtle active={source === 'all'} onClick={() => setSource('all')}>
              All sources
            </FilterChip>
            {sources.map((value) => (
              <FilterChip key={value} subtle active={source === value} onClick={() => setSource(value)}>
                {SOURCE_LABEL[value]}
              </FilterChip>
            ))}
          </div>
        ) : null}

        <PieceFilterDropdown
          tags={allTags}
          selected={tags}
          onToggle={toggleTag}
          onClear={() => setTags(new Set())}
          query={query}
          onQueryChange={setQuery}
        />
      </div>

      <div className="editor-palette-grid">
        {visible.map((item) => (
          <button
            type="button"
            key={`${item.group}:${item.slug}`}
            className={cn('editor-palette-cell', `is-${item.assetSource}`)}
            draggable
            title={item.label}
            aria-label={item.label}
            onDragStart={(event) => setDrag(event, item.payload)}
            onMouseEnter={() => setActiveLabel(item.label)}
            onFocus={() => setActiveLabel(item.label)}
            onMouseLeave={() => setActiveLabel(null)}
            onBlur={() => setActiveLabel(null)}
          >
            <span className="editor-palette-thumb">
              {item.thumb ? <img src={item.thumb} alt="" draggable={false} /> : null}
            </span>
            {item.walkable ? (
              <span className="editor-walkable" title="Blue can walk this landing">
                <Footprints className="size-3" aria-hidden="true" />
              </span>
            ) : null}
          </button>
        ))}
        {visible.length === 0 ? (
          <p className="editor-palette-empty">No pieces match these filters.</p>
        ) : null}
      </div>

      <footer className="editor-palette-foot">
        <button type="button" className="editor-upload-btn" onClick={onUploadClick} disabled={!onUploadClick}>
          <Upload className="size-4" aria-hidden="true" />
          <span>{onUploadClick ? 'Upload a piece' : 'Upload — coming soon'}</span>
        </button>
      </footer>
    </aside>
  )
}

function FilterChip({
  active,
  subtle,
  onClick,
  children,
}: {
  active: boolean
  subtle?: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      className={cn('editor-filter-chip', subtle && 'is-subtle', active && 'is-active')}
      aria-pressed={active}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
