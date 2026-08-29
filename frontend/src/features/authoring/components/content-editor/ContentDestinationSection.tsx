import { Layers, Plus, Settings2 } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Button } from '@/shared/components/Button'
import { ADMIN_ROUTES } from '@/shared/navigation/routes'

type DestinationOption = { id: number; title: string }

type ContentDestinationSectionProps = {
  isOfficialMode: boolean
  chapters: DestinationOption[]
  selectedChapterId: number | null
  createChapterDisabled: boolean
  onDestinationChange: (id: number | null) => void
  onCreateChapter: () => void
}

const DESTINATION_LABEL_ID = 'content-editor-destination-label'

export function ContentDestinationSection({
  isOfficialMode,
  chapters,
  selectedChapterId,
  createChapterDisabled,
  onDestinationChange,
  onCreateChapter,
}: ContentDestinationSectionProps) {
  return (
    <section className="author-card">
      <header className="author-card-head">
        <h2 className="author-card-title" id={DESTINATION_LABEL_ID}>
          <Layers className="size-4" aria-hidden="true" /> {isOfficialMode ? 'Official chapter' : 'Chapter'}
        </h2>
        <p className="author-card-sub">
          {isOfficialMode
            ? 'Choose the real curriculum chapter where this content will compile.'
            : 'Which authored chapter this belongs to. A chapter can hold adventures, challenges, and lessons.'}
        </p>
      </header>
      <div className="author-inline-row author-destination-row">
        <select
          className="author-input"
          aria-labelledby={DESTINATION_LABEL_ID}
          value={selectedChapterId ?? ''}
          onChange={(event) => onDestinationChange(event.target.value ? Number(event.target.value) : null)}
        >
          <option value="" disabled>
            {isOfficialMode ? 'Choose a published chapter' : '— Unassigned —'}
          </option>
          {chapters.map((chapter) => (
            <option key={chapter.id} value={chapter.id}>{chapter.title}</option>
          ))}
        </select>
        {isOfficialMode ? (
          <Button asChild variant="outline" size="sm">
            <Link to={ADMIN_ROUTES.curriculum}>
              <Settings2 className="size-4" aria-hidden="true" /> Manage curriculum
            </Link>
          </Button>
        ) : (
          <Button
            variant="outline"
            size="sm"
            disabled={createChapterDisabled}
            onClick={onCreateChapter}
          >
            <Plus className="size-4" aria-hidden="true" /> New chapter
          </Button>
        )}
        {!isOfficialMode && selectedChapterId ? (
          <Button asChild variant="outline" size="sm">
            <Link to={`/level-editor/chapters/${selectedChapterId}`}>
              <Settings2 className="size-4" aria-hidden="true" /> Edit chapter
            </Link>
          </Button>
        ) : null}
      </div>
      <p className="author-hint">
        {isOfficialMode
          ? 'Published runtime levels and lessons attach directly to this chapter and survive curriculum reseeding.'
          : "Name, overview, and challenge unlock settings live on the chapter's own page."}
      </p>
    </section>
  )
}
