import { CATEGORIES, SUBKINDS, type Category } from '@/features/marketplace/categories'
import { cn } from '@/shared/utils/cn'

export function MarketplaceCategoryRail({
  category,
  subKind,
  onCategory,
  onSubKind,
  ownedOnly,
  onOwnedOnly,
  tags,
  availableTags,
  onToggleTag,
  onClearTags,
}: {
  category: Category
  subKind: string | null
  onCategory: (category: Category) => void
  onSubKind: (subKind: string | null) => void
  ownedOnly: boolean
  onOwnedOnly: (value: boolean) => void
  tags: string[]
  availableTags: string[]
  onToggleTag: (tag: string) => void
  onClearTags: () => void
}) {
  const subKinds = SUBKINDS[category]

  return (
    <div className="market-rail">
      <div className="market-rail-row">
        <nav className="market-cats" aria-label="Shop categories">
          {CATEGORIES.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              className={cn('market-cat', category === id && 'is-active')}
              onClick={() => onCategory(id)}
            >
              <Icon className="size-4" aria-hidden="true" />
              {label}
            </button>
          ))}
        </nav>
        <button
          type="button"
          className={cn('market-owned-toggle', ownedOnly && 'is-active')}
          onClick={() => onOwnedOnly(!ownedOnly)}
        >
          {ownedOnly ? 'Owned' : 'Available'}
        </button>
      </div>

      {subKinds.length ? (
        <div className="market-subkinds">
          <button
            type="button"
            className={cn('market-chip', subKind === null && 'is-active')}
            onClick={() => onSubKind(null)}
          >
            All
          </button>
          {subKinds.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              className={cn('market-chip', subKind === id && 'is-active')}
              onClick={() => onSubKind(id)}
            >
              <Icon className="size-3.5" aria-hidden="true" />
              {label}
            </button>
          ))}
        </div>
      ) : null}

      {availableTags.length ? (
        <div className="market-tags" aria-label="Filter by tag">
          <span className="market-tags-label">Tags</span>
          {availableTags.map((tag) => (
            <button
              key={tag}
              type="button"
              aria-pressed={tags.includes(tag)}
              className={cn('market-chip market-chip--tag', tags.includes(tag) && 'is-active')}
              onClick={() => onToggleTag(tag)}
            >
              {tag}
            </button>
          ))}
          {tags.length ? (
            <button type="button" className="market-chip market-chip--clear" onClick={onClearTags}>
              Clear
            </button>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
