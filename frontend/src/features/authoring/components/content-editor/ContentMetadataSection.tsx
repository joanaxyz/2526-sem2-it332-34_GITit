import { TagsField } from '@/features/authoring/components/TagsField'
import type { ContentKind, Visibility } from '@/features/authoring/types'
import { DIFFICULTIES, VISIBILITIES } from '@/features/authoring/utils/authoringModel'

type ContentMetadataSectionProps = {
  sourceKey: string
  kind: ContentKind
  title: string
  slug: string
  summary: string
  commandFamily: string
  difficulty: string
  tags: string[]
  visibility: Visibility
  onTitleChange: (value: string) => void
  onSlugChange: (value: string) => void
  onSummaryChange: (value: string) => void
  onCommandFamilyChange: (value: string) => void
  onDifficultyChange: (value: string) => void
  onTagsChange: (value: string[]) => void
  onVisibilityChange: (value: Visibility) => void
}

export function ContentMetadataSection({
  sourceKey,
  kind,
  title,
  slug,
  summary,
  commandFamily,
  difficulty,
  tags,
  visibility,
  onTitleChange,
  onSlugChange,
  onSummaryChange,
  onCommandFamilyChange,
  onDifficultyChange,
  onTagsChange,
  onVisibilityChange,
}: ContentMetadataSectionProps) {
  return (
    <section className="author-card">
      <div className="author-grid-2">
        <label className="author-field">
          <span className="author-label">Title</span>
          <input className="author-input" value={title} onChange={(event) => onTitleChange(event.target.value)} />
        </label>
        <label className="author-field">
          <span className="author-label">Slug</span>
          <input className="author-input" value={slug} onChange={(event) => onSlugChange(event.target.value)} />
        </label>
      </div>
      <label className="author-field">
        <span className="author-label">Summary</span>
        <textarea
          className="author-input"
          rows={2}
          value={summary}
          onChange={(event) => onSummaryChange(event.target.value)}
        />
      </label>
      {kind !== 'lesson' ? (
        <div className="author-grid-2">
          <label className="author-field">
            <span className="author-label">Command family</span>
            <input
              className="author-input"
              value={commandFamily}
              onChange={(event) => onCommandFamilyChange(event.target.value)}
              placeholder="git status"
            />
          </label>
          <label className="author-field">
            <span className="author-label">Difficulty</span>
            <select
              className="author-input"
              value={difficulty}
              onChange={(event) => onDifficultyChange(event.target.value)}
            >
              {DIFFICULTIES.map((option) => (
                <option key={option.id} value={option.id}>{option.label}</option>
              ))}
            </select>
          </label>
        </div>
      ) : null}
      <div className="author-grid-2">
        <TagsField key={sourceKey} value={tags} onChange={onTagsChange} />
        <label className="author-field">
          <span className="author-label">Visibility</span>
          <select
            className="author-input"
            value={visibility}
            onChange={(event) => onVisibilityChange(event.target.value as Visibility)}
          >
            {VISIBILITIES.map((option) => (
              <option key={option.id} value={option.id}>{option.label}</option>
            ))}
          </select>
        </label>
      </div>
    </section>
  )
}
