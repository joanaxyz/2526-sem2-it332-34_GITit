import { ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'

import type { CommandFormOption } from '@/features/authoring/api/authoringApi'
import {
  emptyLevel,
  type AuthoredLevel,
} from '@/features/authoring/utils/authoringModel'
import type { ContentKind } from '@/features/authoring/types'
import { CommandFormPicker } from '@/features/authoring/components/levels-editor/CommandFormPicker'
import { ProblemsEditor } from '@/features/authoring/components/levels-editor/ProblemsEditor'

/** Structured editor for an adventure/challenge's levels.
 *
 * A level groups ordered problems: for an adventure a problem is a playable
 * WAVE, for a challenge a difficulty TRIAL. Each problem owns its scenario and
 * its own extra variants. */
export function LevelsEditor({
  kind,
  levels,
  onChange,
  commandFormOptions = [],
}: {
  kind: ContentKind
  levels: AuthoredLevel[]
  onChange: (levels: AuthoredLevel[]) => void
  commandFormOptions?: CommandFormOption[]
}) {
  const problemNoun = kind === 'challenge' ? 'trial' : 'wave'
  const [collapsedLevels, setCollapsedLevels] = useState<Set<number>>(
    () => new Set(levels.map((_, index) => index).filter((index) => index > 0)),
  )

  function patch(index: number, next: Partial<AuthoredLevel>) {
    onChange(levels.map((level, i) => (i === index ? { ...level, ...next } : level)))
  }
  function addLevel() {
    onChange([...levels, emptyLevel(kind, levels.length)])
  }
  function removeLevel(index: number) {
    if (!window.confirm(`Remove level ${index + 1}?`)) return
    onChange(levels.filter((_, i) => i !== index))
    setCollapsedLevels((current) => {
      const next = new Set<number>()
      for (const value of current) {
        if (value < index) next.add(value)
        if (value > index) next.add(value - 1)
      }
      return next
    })
  }
  function toggleLevel(index: number) {
    setCollapsedLevels((current) => {
      const next = new Set(current)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Levels</h2>
        <p className="author-card-sub">
          A level is a lesson stage. It groups ordered {problemNoun}s — each {problemNoun} is one
          playable Git problem with its own variants.
        </p>
      </header>

      {levels.map((level, index) => (
        <div className={collapsedLevels.has(index) ? 'author-level is-collapsed' : 'author-level'} key={index}>
          <div className="author-level-head">
            <button
              type="button"
              className="author-level-toggle"
              onClick={() => toggleLevel(index)}
              aria-expanded={!collapsedLevels.has(index)}
            >
              {collapsedLevels.has(index) ? (
                <ChevronDown className="size-4" aria-hidden="true" />
              ) : (
                <ChevronUp className="size-4" aria-hidden="true" />
              )}
              <span className="author-level-title">Level {index + 1}</span>
              <span className="author-level-summary">
                {level.title || 'Untitled'} · {level.problems.length} {problemNoun}
                {level.problems.length === 1 ? '' : 's'}
              </span>
            </button>
            <div className="author-level-actions">
              {levels.length > 1 ? (
                <button type="button" className="author-icon-btn" onClick={() => removeLevel(index)} aria-label="Remove level">
                  <Trash2 className="size-4" aria-hidden="true" />
                </button>
              ) : null}
            </div>
          </div>

          {collapsedLevels.has(index) ? null : (
            <>
              <div className="author-grid-2">
                <label className="author-field">
                  <span className="author-label">Title</span>
                  <input className="author-input" value={level.title} onChange={(e) => patch(index, { title: e.target.value })} />
                </label>
                <label className="author-field">
                  <span className="author-label">Slug</span>
                  <input className="author-input" value={level.slug} onChange={(e) => patch(index, { slug: e.target.value })} />
                </label>
              </div>

              <label className="author-field">
                <span className="author-label">Lesson brief (optional)</span>
                <span className="author-hint">A short intro shown above this level's problems.</span>
                <textarea
                  className="author-input"
                  rows={2}
                  value={level.brief}
                  onChange={(e) => patch(index, { brief: e.target.value })}
                  placeholder="In this level you'll make your first save…"
                />
              </label>

              <CommandFormPicker
                options={commandFormOptions}
                selected={level.commandForms}
                onChange={(commandForms) => patch(index, { commandForms })}
              />

              <ProblemsEditor
                kind={kind}
                problems={level.problems}
                onChange={(problems) => patch(index, { problems })}
              />
            </>
          )}
        </div>
      ))}

      <button type="button" className="author-add-btn" onClick={addLevel}>
        <Plus className="size-4" aria-hidden="true" /> Add level
      </button>
    </section>
  )
}

