import { Plus, Trash2 } from 'lucide-react'

import { MonsterSelect } from '@/features/authoring/components/MonsterRosterField'
import { useOwnedMonsters } from '@/features/authoring/components/useOwnedMonsters'
import {
  EVALUATION_MODES,
  emptyLevel,
  emptyVariant,
  type AuthoredLevel,
} from '@/features/authoring/authoringModel'
import type { ContentKind } from '@/features/authoring/types'

const DIFFICULTIES = ['easy', 'medium', 'hard']

/** Structured editor for an adventure/challenge's levels (replaces raw JSON). */
export function LevelsEditor({
  kind,
  levels,
  onChange,
}: {
  kind: ContentKind
  levels: AuthoredLevel[]
  onChange: (levels: AuthoredLevel[]) => void
}) {
  const { monsters } = useOwnedMonsters()

  function patch(index: number, next: Partial<AuthoredLevel>) {
    onChange(levels.map((level, i) => (i === index ? { ...level, ...next } : level)))
  }
  function addLevel() {
    onChange([...levels, emptyLevel(kind, levels.length)])
  }
  function removeLevel(index: number) {
    onChange(levels.filter((_, i) => i !== index))
  }

  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title">Levels</h2>
        <p className="author-card-sub">Each level is one playable challenge in this storey.</p>
      </header>

      {levels.map((level, index) => (
        <div className="author-level" key={index}>
          <div className="author-level-head">
            <h3 className="author-level-title">Level {index + 1}</h3>
            {levels.length > 1 ? (
              <button type="button" className="author-icon-btn" onClick={() => removeLevel(index)} aria-label="Remove level">
                <Trash2 className="size-4" aria-hidden="true" />
              </button>
            ) : null}
          </div>

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

          {kind === 'challenge' ? (
            <label className="author-field">
              <span className="author-label">Difficulty</span>
              <select className="author-input" value={level.difficulty} onChange={(e) => patch(index, { difficulty: e.target.value })}>
                {DIFFICULTIES.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>
          ) : null}

          <CommandListField
            label="Solution commands"
            commands={level.solutionCommands}
            onChange={(solutionCommands) => patch(index, { solutionCommands })}
          />

          <label className="author-field">
            <span className="author-label">Starting repository state (JSON)</span>
            <span className="author-hint">The repo the player begins from. Leave as {'{}'} for an empty repo.</span>
            <textarea
              className="author-input author-mono"
              rows={4}
              spellCheck={false}
              value={level.initialStateText}
              onChange={(e) => patch(index, { initialStateText: e.target.value })}
            />
          </label>

          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Completion</span>
              <select
                className="author-input"
                value={level.evaluationMode}
                onChange={(e) => patch(index, { evaluationMode: e.target.value })}
              >
                {EVALUATION_MODES.map((mode) => (
                  <option key={mode.id} value={mode.id}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="author-field">
              <span className="author-label">Successes to master</span>
              <input
                className="author-input"
                type="number"
                min={1}
                value={level.requiredSuccessfulAttempts}
                onChange={(e) => patch(index, { requiredSuccessfulAttempts: Number(e.target.value) })}
              />
            </label>
          </div>

          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Min commands</span>
              <input
                className="author-input"
                type="number"
                min={1}
                value={level.minCountedCommands}
                onChange={(e) => patch(index, { minCountedCommands: Number(e.target.value) })}
              />
            </label>
            <label className="author-field">
              <span className="author-label">Max commands (budget)</span>
              <input
                className="author-input"
                type="number"
                min={1}
                value={level.maxCountedCommands}
                onChange={(e) => patch(index, { maxCountedCommands: Number(e.target.value) })}
              />
            </label>
          </div>

          <EncounterEditor
            level={level}
            monsters={monsters}
            onChange={(next) => patch(index, next)}
            showBoss={kind === 'challenge'}
          />

          <VariantsEditor level={level} onChange={(variants) => patch(index, { variants })} />
        </div>
      ))}

      <button type="button" className="author-add-btn" onClick={addLevel}>
        <Plus className="size-4" aria-hidden="true" /> Add level
      </button>
    </section>
  )
}

function CommandListField({
  label,
  commands,
  onChange,
}: {
  label: string
  commands: string[]
  onChange: (commands: string[]) => void
}) {
  return (
    <div className="author-field">
      <span className="author-label">{label}</span>
      {commands.map((command, index) => (
        <div className="author-inline-row" key={index}>
          <input
            className="author-input author-mono"
            value={command}
            onChange={(e) => onChange(commands.map((c, i) => (i === index ? e.target.value : c)))}
            placeholder="git commit -m ..."
          />
          {commands.length > 1 ? (
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => onChange(commands.filter((_, i) => i !== index))}
              aria-label="Remove command"
            >
              <Trash2 className="size-4" aria-hidden="true" />
            </button>
          ) : null}
        </div>
      ))}
      <button type="button" className="author-add-btn" onClick={() => onChange([...commands, ''])}>
        <Plus className="size-4" aria-hidden="true" /> Add command
      </button>
    </div>
  )
}

function EncounterEditor({
  level,
  monsters,
  onChange,
  showBoss,
}: {
  level: AuthoredLevel
  monsters: ReturnType<typeof useOwnedMonsters>['monsters']
  onChange: (next: Partial<AuthoredLevel>) => void
  showBoss: boolean
}) {
  function setRow(index: number, key: 'species' | 'hp', value: string | number) {
    onChange({
      encounterSpec: level.encounterSpec.map((row, i) => (i === index ? { ...row, [key]: value } : row)),
    })
  }
  function addRow() {
    const species = monsters[0]?.slug ?? ''
    onChange({ encounterSpec: [...level.encounterSpec, { species, hp: 1 }] })
  }
  function removeRow(index: number) {
    onChange({ encounterSpec: level.encounterSpec.filter((_, i) => i !== index) })
  }

  return (
    <div className="author-field">
      <span className="author-label">Encounter monsters</span>
      <span className="author-hint">Pick from your roster. Leave empty to use the storey's mob roster.</span>
      {level.encounterSpec.map((row, index) => (
        <div className="author-inline-row" key={index}>
          <MonsterSelect value={row.species} monsters={monsters} onChange={(species) => setRow(index, 'species', species)} />
          <input
            className="author-input author-input--narrow"
            type="number"
            min={1}
            value={row.hp}
            onChange={(e) => setRow(index, 'hp', Number(e.target.value))}
            aria-label="HP"
          />
          <button type="button" className="author-icon-btn" onClick={() => removeRow(index)} aria-label="Remove monster">
            <Trash2 className="size-4" aria-hidden="true" />
          </button>
        </div>
      ))}
      <button type="button" className="author-add-btn" onClick={addRow} disabled={monsters.length === 0}>
        <Plus className="size-4" aria-hidden="true" /> Add monster
      </button>

      {showBoss ? (
        <div className="author-boss">
          <span className="author-label">Boss</span>
          <div className="author-inline-row">
            <MonsterSelect
              value={level.bossSpec?.species ?? ''}
              monsters={monsters}
              allowEmpty
              onChange={(species) =>
                onChange({ bossSpec: species ? { species, hp: level.bossSpec?.hp ?? 6 } : null })
              }
            />
            {level.bossSpec?.species ? (
              <input
                className="author-input author-input--narrow"
                type="number"
                min={1}
                value={level.bossSpec.hp}
                onChange={(e) => onChange({ bossSpec: { species: level.bossSpec!.species, hp: Number(e.target.value) } })}
                aria-label="Boss HP"
              />
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  )
}

function VariantsEditor({
  level,
  onChange,
}: {
  level: AuthoredLevel
  onChange: (variants: AuthoredLevel['variants']) => void
}) {
  function patch(index: number, next: Partial<AuthoredLevel['variants'][number]>) {
    onChange(level.variants.map((variant, i) => (i === index ? { ...variant, ...next } : variant)))
  }

  return (
    <div className="author-field">
      <span className="author-label">Extra test cases (optional)</span>
      <span className="author-hint">Each adds another starting repo + solution the level can present.</span>
      {level.variants.map((variant, index) => (
        <div className="author-variant" key={index}>
          <div className="author-inline-row">
            <input
              className="author-input"
              value={variant.label}
              onChange={(e) => patch(index, { label: e.target.value })}
              placeholder="Case label"
            />
            <button
              type="button"
              className="author-icon-btn"
              onClick={() => onChange(level.variants.filter((_, i) => i !== index))}
              aria-label="Remove test case"
            >
              <Trash2 className="size-4" aria-hidden="true" />
            </button>
          </div>
          <textarea
            className="author-input author-mono"
            rows={3}
            spellCheck={false}
            value={variant.initialStateText}
            onChange={(e) => patch(index, { initialStateText: e.target.value })}
            placeholder="Starting state JSON"
          />
          <input
            className="author-input author-mono"
            value={variant.solutionCommands.join(' && ')}
            onChange={(e) => patch(index, { solutionCommands: e.target.value.split('&&').map((s) => s.trim()) })}
            placeholder="git add . && git commit -m ..."
          />
        </div>
      ))}
      <button type="button" className="author-add-btn" onClick={() => onChange([...level.variants, emptyVariant(level.variants.length)])}>
        <Plus className="size-4" aria-hidden="true" /> Add test case
      </button>
    </div>
  )
}
