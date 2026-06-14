import { useEffect, useRef, useState } from 'react'
import { Check, ListFilter, Search, X } from 'lucide-react'

import { cn } from '@/shared/utils/cn'

/**
 * Scalable replacement for the old one-chip-per-tag row. Tags live behind a
 * single popover with an internal search, so the palette stays compact no matter
 * how many tags the asset library grows to. The tag list is derived from the
 * assets actually present, so new DB tags appear automatically. The search also
 * filters the piece grid (by label or tag), wired through `query` in the parent.
 */
export function PieceFilterDropdown({
  tags,
  selected,
  onToggle,
  onClear,
  query,
  onQueryChange,
}: {
  tags: string[]
  selected: Set<string>
  onToggle: (tag: string) => void
  onClear: () => void
  query: string
  onQueryChange: (value: string) => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!open) return
    function onPointerDown(event: PointerEvent) {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false)
    }
    window.addEventListener('pointerdown', onPointerDown)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('pointerdown', onPointerDown)
      window.removeEventListener('keydown', onKey)
    }
  }, [open])

  const needle = query.trim().toLowerCase()
  const shownTags = needle ? tags.filter((tag) => tag.toLowerCase().includes(needle)) : tags
  const activeCount = selected.size + (needle ? 1 : 0)

  return (
    <div className="editor-filter" ref={rootRef}>
      <button
        type="button"
        className={cn('editor-filter-trigger', activeCount > 0 && 'is-active')}
        aria-expanded={open}
        aria-haspopup="true"
        onClick={() => setOpen((v) => !v)}
      >
        <ListFilter className="size-3.5" aria-hidden="true" />
        <span>Filter</span>
        {activeCount > 0 ? <span className="editor-filter-count">{activeCount}</span> : null}
      </button>

      {open ? (
        <div className="editor-filter-pop" role="dialog" aria-label="Filter pieces">
          <label className="editor-filter-search">
            <Search className="size-3.5" aria-hidden="true" />
            <input
              type="search"
              value={query}
              autoFocus
              placeholder="Search pieces or tags…"
              onChange={(event) => onQueryChange(event.target.value)}
            />
            {query ? (
              <button type="button" className="editor-filter-search-clear" aria-label="Clear search" onClick={() => onQueryChange('')}>
                <X className="size-3.5" aria-hidden="true" />
              </button>
            ) : null}
          </label>

          {tags.length ? (
            <>
              <div className="editor-filter-list" role="group" aria-label="Filter by tag">
                {shownTags.map((tag) => {
                  const isOn = selected.has(tag)
                  return (
                    <button
                      key={tag}
                      type="button"
                      className={cn('editor-filter-option', isOn && 'is-on')}
                      aria-pressed={isOn}
                      onClick={() => onToggle(tag)}
                    >
                      <span className="editor-filter-check" aria-hidden="true">
                        {isOn ? <Check className="size-3" /> : null}
                      </span>
                      <span className="editor-filter-tag">#{tag}</span>
                    </button>
                  )
                })}
                {shownTags.length === 0 ? <p className="editor-filter-none">No tags match “{query}”.</p> : null}
              </div>

              {selected.size > 0 ? (
                <button type="button" className="editor-filter-clear" onClick={onClear}>
                  Clear {selected.size} tag{selected.size > 1 ? 's' : ''}
                </button>
              ) : null}
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
