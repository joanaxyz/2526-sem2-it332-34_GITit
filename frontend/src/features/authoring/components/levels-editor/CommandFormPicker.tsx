import { useMemo, useState } from 'react'

import type { CommandFormOption } from '@/features/authoring/api/authoringApi'


/** Pick the command forms a level introduces and reuses. Listing a form on
 *  several levels is the spiral — its mastery target counts the levels that use
 *  it, so foundational commands are only mastered once practised across many. */
export function CommandFormPicker({
  options,
  selected,
  onChange,
}: {
  options: CommandFormOption[]
  selected: number[]
  onChange: (ids: number[]) => void
}) {
  const [query, setQuery] = useState('')

  const selectedSet = useMemo(() => new Set(selected), [selected])
  const selectedOptions = useMemo(
    () => options.filter((option) => selectedSet.has(option.id)),
    [options, selectedSet],
  )
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return options
    return options.filter(
      (option) =>
        option.usage_form.toLowerCase().includes(q) ||
        option.label.toLowerCase().includes(q) ||
        option.skill_title.toLowerCase().includes(q),
    )
  }, [options, query])

  function toggle(id: number) {
    onChange(selectedSet.has(id) ? selected.filter((value) => value !== id) : [...selected, id])
  }

  if (options.length === 0) {
    return (
      <div className="author-field">
        <span className="author-label">Commands taught & reused</span>
        <span className="author-hint">
          The command catalog is unavailable, so this level will credit a single command derived from
          its content. (Seeded curriculum sets these explicitly.)
        </span>
      </div>
    )
  }

  return (
    <div className="author-field">
      <span className="author-label">Commands taught & reused</span>
      <span className="author-hint">
        Pick every command this level practises — including ones introduced earlier that you want to
        reinforce here. Each selected command earns one solve toward its mastery when this level is
        cleared.
      </span>

      {selectedOptions.length ? (
        <div className="author-inline-row" style={{ flexWrap: 'wrap', gap: 6 }}>
          {selectedOptions.map((option) => (
            <button
              key={option.id}
              type="button"
              className="author-chip is-active"
              onClick={() => toggle(option.id)}
              title="Remove"
            >
              {option.usage_form} ✕
            </button>
          ))}
        </div>
      ) : null}

      <input
        className="author-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Filter commands… (e.g. git add)"
      />
      <div className="author-form-catalog" style={{ maxHeight: 180, overflowY: 'auto' }}>
        {filtered.slice(0, 60).map((option) => (
          <button
            key={option.id}
            type="button"
            className={selectedSet.has(option.id) ? 'author-chip is-active' : 'author-chip'}
            onClick={() => toggle(option.id)}
          >
            <span className="author-mono">{option.usage_form}</span>
            <span className="author-hint" style={{ marginLeft: 6 }}>
              {option.skill_title}
              {option.chapter_number ? ` · ch${option.chapter_number}` : ''}
            </span>
          </button>
        ))}
        {filtered.length === 0 ? <span className="author-hint">No commands match “{query}”.</span> : null}
      </div>
    </div>
  )
}
