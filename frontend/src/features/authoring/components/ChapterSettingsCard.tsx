import type { AuthoringChapter } from '@/features/authoring/types'

type ChapterPatch = Partial<
  Pick<AuthoringChapter, 'title' | 'summary'>
>

/**
 * The chapter (floor) form: name and overview. These are shared by every adventure/challenge/lesson in the chapter,
 * so they live on the dedicated chapter page rather than inside any one content editor.
 *
 * Note: GitCoin reward checkpoints are deliberately NOT authorable here. Coins
 * are reserved for the official story; custom stories grant no coins.
 */
export function ChapterSettingsCard({
  chapter,
  onChange,
}: {
  chapter: AuthoringChapter
  onChange: (patch: ChapterPatch) => void
}) {
  return (
    <section className="author-card">
      <label className="author-field">
        <span className="author-label">Chapter name</span>
        <input className="author-input" value={chapter.title} onChange={(e) => onChange({ title: e.target.value })} />
      </label>

      <label className="author-field">
        <span className="author-label">Overview</span>
        <span className="author-hint">Shown on this chapter's map panel — describe what this chapter teaches.</span>
        <textarea
          className="author-input"
          rows={3}
          value={chapter.summary ?? ''}
          onChange={(e) => onChange({ summary: e.target.value })}
        />
      </label>

      <p className="author-hint author-coins-note">
        Custom stories don't grant GitCoins — progress reward chests are reserved for the official story.
      </p>

    </section>
  )
}
