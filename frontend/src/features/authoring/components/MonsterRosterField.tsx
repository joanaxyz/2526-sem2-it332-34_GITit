import type { MonsterAssetDescriptor } from '@/shared/assets/types'
import { cn } from '@/shared/utils/cn'

/** A multi-select roster of monster slugs rendered as toggle chips. */
export function MonsterRosterField({
  label,
  hint,
  monsters,
  selected,
  onChange,
}: {
  label: string
  hint?: string
  monsters: MonsterAssetDescriptor[]
  selected: string[]
  onChange: (slugs: string[]) => void
}) {
  function toggle(slug: string) {
    onChange(selected.includes(slug) ? selected.filter((s) => s !== slug) : [...selected, slug])
  }

  return (
    <div className="author-field">
      <span className="author-label">{label}</span>
      {hint ? <span className="author-hint">{hint}</span> : null}
      <div className="author-chip-row">
        {monsters.map((monster) => (
          <button
            type="button"
            key={monster.slug}
            className={cn('author-chip', selected.includes(monster.slug) && 'is-active')}
            aria-pressed={selected.includes(monster.slug)}
            onClick={() => toggle(monster.slug)}
          >
            {monster.label}
            {monster.source && monster.source !== 'official' ? (
              <span className="author-chip-tag">{monster.source === 'owned' ? 'yours' : 'bought'}</span>
            ) : null}
          </button>
        ))}
        {monsters.length === 0 ? <span className="author-hint">No monsters available yet.</span> : null}
      </div>
    </div>
  )
}

/** A single-monster <select>, used for an encounter row or a boss. */
export function MonsterSelect({
  value,
  monsters,
  onChange,
  allowEmpty,
}: {
  value: string
  monsters: MonsterAssetDescriptor[]
  onChange: (slug: string) => void
  allowEmpty?: boolean
}) {
  return (
    <select className="author-input" value={value} onChange={(event) => onChange(event.target.value)}>
      {allowEmpty ? <option value="">— none —</option> : null}
      {monsters.map((monster) => (
        <option key={monster.slug} value={monster.slug}>
          {monster.label}
          {monster.source && monster.source !== 'official' ? ` (${monster.source})` : ''}
        </option>
      ))}
    </select>
  )
}
