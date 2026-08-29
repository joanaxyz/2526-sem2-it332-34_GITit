import { ChevronDown, ChevronUp, Plus, Trash2 } from 'lucide-react'
import { useMemo } from 'react'

import { EVALUATION_MODES, emptyProblem, emptyVariant, type AuthoredProblem } from '@/features/authoring/utils/authoringModel'
import type { ContentKind } from '@/features/authoring/types'

const DIFFICULTIES = ['easy', 'medium', 'hard']

export function ProblemsEditor({
  kind,
  problems,
  onChange,
}: {
  kind: ContentKind
  problems: AuthoredProblem[]
  onChange: (problems: AuthoredProblem[]) => void
}) {
  const problemNoun = kind === 'challenge' ? 'trial' : 'wave'

  function patch(index: number, next: Partial<AuthoredProblem>) {
    onChange(problems.map((problem, i) => (i === index ? { ...problem, ...next } : problem)))
  }
  function addProblem() {
    onChange([...problems, emptyProblem(kind, problems.length)])
  }
  function removeProblem(index: number) {
    if (!window.confirm(`Remove ${problemNoun} ${index + 1}?`)) return
    onChange(problems.filter((_, i) => i !== index))
  }
  function moveProblem(index: number, direction: -1 | 1) {
    const nextIndex = index + direction
    if (nextIndex < 0 || nextIndex >= problems.length) return
    const next = [...problems]
    const [problem] = next.splice(index, 1)
    next.splice(nextIndex, 0, problem)
    onChange(next)
  }

  return (
    <div className="author-field">
      <span className="author-label">{kind === 'challenge' ? 'Trials' : 'Waves'}</span>
      <span className="author-hint">
        {kind === 'challenge'
          ? 'Difficulty tiers for this stage. Harder trials expect more complex repository changes.'
          : 'Ordered playable problems. The player clears them in sequence to finish the level.'}
      </span>

      {problems.map((problem, index) => (
        <div className="author-variant" key={index}>
          <div className="author-inline-row">
            <span className="author-label">
              {kind === 'challenge' ? 'Trial' : 'Wave'} {index + 1}
            </span>
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => moveProblem(index, -1)}
              disabled={index === 0}
              aria-label="Move up"
            >
              <ChevronUp className="size-4" aria-hidden="true" />
            </button>
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => moveProblem(index, 1)}
              disabled={index === problems.length - 1}
              aria-label="Move down"
            >
              <ChevronDown className="size-4" aria-hidden="true" />
            </button>
            {problems.length > 1 ? (
              <button type="button" className="author-icon-btn" onClick={() => removeProblem(index)} aria-label="Remove">
                <Trash2 className="size-4" aria-hidden="true" />
              </button>
            ) : null}
          </div>

          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Title</span>
              <input className="author-input" value={problem.title} onChange={(e) => patch(index, { title: e.target.value })} />
            </label>
            <label className="author-field">
              <span className="author-label">Slug</span>
              <input className="author-input" value={problem.slug} onChange={(e) => patch(index, { slug: e.target.value })} />
            </label>
          </div>

          {kind === 'challenge' ? (
            <label className="author-field">
              <span className="author-label">Difficulty</span>
              <select className="author-input" value={problem.difficulty} onChange={(e) => patch(index, { difficulty: e.target.value })}>
                {DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Story</span>
              <span className="author-hint">The fiction that frames the puzzle.</span>
              <textarea
                className="author-input"
                rows={2}
                value={problem.story}
                onChange={(e) => patch(index, { story: e.target.value })}
                placeholder="The team's history got tangled…"
              />
            </label>
            <label className="author-field">
              <span className="author-label">Task</span>
              <span className="author-hint">The concrete thing the player must do.</span>
              <textarea
                className="author-input"
                rows={2}
                value={problem.task}
                onChange={(e) => patch(index, { task: e.target.value })}
                placeholder="Stage README.md and commit it."
              />
            </label>
          </div>

          <CommandListField
            label="Solution commands"
            commands={problem.solutionCommands}
            onChange={(solutionCommands) => patch(index, { solutionCommands })}
          />

          <JsonObjectField
            label="Starting repository state (JSON)"
            hint="The repo the player begins from. Leave as {} for an empty repo. (Advanced escape hatch — a guided builder is planned.)"
            rows={4}
            value={problem.initialStateText}
            onChange={(initialStateText) => patch(index, { initialStateText })}
          />

          <label className="author-field">
            <span className="author-label">Completion</span>
            <select
              className="author-input"
              value={problem.evaluationMode}
              onChange={(e) => patch(index, { evaluationMode: e.target.value })}
            >
              {EVALUATION_MODES.map((mode) => (
                <option key={mode.id} value={mode.id}>
                  {mode.label}
                </option>
              ))}
            </select>
          </label>

          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Min commands</span>
              <input
                className="author-input"
                type="number"
                min={1}
                value={problem.minCountedCommands}
                onChange={(e) => patch(index, { minCountedCommands: Number(e.target.value) })}
              />
            </label>
            <label className="author-field">
              <span className="author-label">Command budget</span>
              <input
                className="author-input"
                type="number"
                min={1}
                value={problem.maxCountedCommands}
                onChange={(e) => patch(index, { maxCountedCommands: Number(e.target.value) })}
              />
            </label>
          </div>

          <VariantsEditor problem={problem} onChange={(variants) => patch(index, { variants })} />
        </div>
      ))}

      <button type="button" className="author-add-btn" onClick={addProblem}>
        <Plus className="size-4" aria-hidden="true" /> Add {problemNoun}
      </button>
    </div>
  )
}

function CommandListField({
  label,
  hint,
  commands,
  onChange,
  placeholder = 'git commit -m ...',
  mono = true,
  addLabel = 'Add command',
  removeLabel = 'Remove command',
  minRows = 1,
}: {
  label: string
  hint?: string
  commands: string[]
  onChange: (commands: string[]) => void
  placeholder?: string
  mono?: boolean
  addLabel?: string
  removeLabel?: string
  /** When 0, the last row can be removed. */
  minRows?: number
}) {
  return (
    <div className="author-field">
      <span className="author-label">{label}</span>
      {hint ? <span className="author-hint">{hint}</span> : null}
      {commands.map((command, index) => (
        <div className="author-inline-row" key={index}>
          <input
            className={mono ? 'author-input author-mono' : 'author-input'}
            value={command}
            onChange={(e) => onChange(commands.map((c, i) => (i === index ? e.target.value : c)))}
            placeholder={placeholder}
          />
          {commands.length > minRows ? (
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => onChange(commands.filter((_, i) => i !== index))}
              aria-label={removeLabel}
            >
              <Trash2 className="size-4" aria-hidden="true" />
            </button>
          ) : null}
        </div>
      ))}
      <button type="button" className="author-add-btn" onClick={() => onChange([...commands, ''])}>
        <Plus className="size-4" aria-hidden="true" /> {addLabel}
      </button>
    </div>
  )
}

/** Raw-JSON repository-state escape hatch with live validity feedback and a
 *  pretty-print helper, so a bad paste is caught here rather than at save. */
function JsonObjectField({
  label,
  hint,
  value,
  onChange,
  rows,
}: {
  label: string
  hint?: string
  value: string
  onChange: (value: string) => void
  rows: number
}) {
  const error = useMemo(() => {
    const trimmed = value.trim()
    if (!trimmed) return null
    let parsed: unknown
    try {
      parsed = JSON.parse(trimmed)
    } catch {
      return 'Not valid JSON yet.'
    }
    if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
      return 'Must be a JSON object, e.g. {}.'
    }
    return null
  }, [value])

  function format() {
    try {
      onChange(JSON.stringify(JSON.parse(value), null, 2))
    } catch {
      /* not parseable — leave the author's text untouched */
    }
  }

  return (
    <div className="author-field">
      <div className="author-inline-row" style={{ justifyContent: 'space-between' }}>
        <span className="author-label">{label}</span>
        <button type="button" className="author-add-btn" onClick={format} disabled={Boolean(error) || !value.trim()}>
          Format
        </button>
      </div>
      {hint ? <span className="author-hint">{hint}</span> : null}
      <textarea
        className="author-input author-mono"
        rows={rows}
        spellCheck={false}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={error ? { borderColor: 'hsl(var(--destructive))' } : undefined}
        aria-invalid={Boolean(error)}
      />
      {error ? (
        <span className="author-hint" role="alert" style={{ color: 'hsl(var(--destructive))' }}>
          {error}
        </span>
      ) : null}
    </div>
  )
}

function VariantsEditor({
  problem,
  onChange,
}: {
  problem: AuthoredProblem
  onChange: (variants: AuthoredProblem['variants']) => void
}) {
  function patch(index: number, next: Partial<AuthoredProblem['variants'][number]>) {
    onChange(problem.variants.map((variant, i) => (i === index ? { ...variant, ...next } : variant)))
  }

  return (
    <div className="author-field">
      <span className="author-label">Variants (extra cases)</span>
      <span className="author-hint">
        Each is another starting repo + solution for the same problem. On a retry the player is served a
        different variant, so add a few to keep retries fresh.
      </span>
      {problem.variants.map((variant, index) => (
        <div className="author-variant" key={index}>
          <div className="author-inline-row">
            <input
              className="author-input"
              value={variant.label}
              onChange={(e) => patch(index, { label: e.target.value })}
              placeholder="Variant label"
            />
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => onChange(problem.variants.filter((_, i) => i !== index))}
              aria-label="Remove variant"
            >
              <Trash2 className="size-4" aria-hidden="true" />
            </button>
          </div>
          <JsonObjectField
            label="Starting repository state (JSON)"
            rows={3}
            value={variant.initialStateText}
            onChange={(initialStateText) => patch(index, { initialStateText })}
          />
          <CommandListField
            label="Solution commands"
            commands={variant.solutionCommands}
            onChange={(solutionCommands) => patch(index, { solutionCommands })}
          />
        </div>
      ))}
      <button type="button" className="author-add-btn" onClick={() => onChange([...problem.variants, emptyVariant(problem.variants.length)])}>
        <Plus className="size-4" aria-hidden="true" /> Add variant
      </button>
    </div>
  )
}
