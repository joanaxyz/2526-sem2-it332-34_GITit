import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Layers, Save } from 'lucide-react'
import { useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import { ChapterSettingsCard } from '@/features/authoring/components/ChapterSettingsCard'
import { useUnsavedChangesGuard } from '@/features/authoring/hooks/useUnsavedChangesGuard'
import type { AuthoringChapter } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

/** A blank chapter draft for the create flow. `index` (1-based) presets the
 *  default name and sort order when the floor slot is known. */
function blankChapter(index: number): AuthoringChapter {
  const hasIndex = Number.isInteger(index) && index > 0
  return {
    id: 0,
    owner_id: null,
    slug: '',
    title: hasIndex ? `Chapter ${index}` : '',
    summary: '',
    sort_order: hasIndex ? index - 1 : 0,
    created_at: '',
    updated_at: '',
  }
}

function sameChapter(a: AuthoringChapter, b: AuthoringChapter): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

/**
 * Dedicated chapter (floor) page: create a new chapter or edit an existing one's
 * name, overview, and challenge unlock settings. Chapter settings are shared across all
 * content in the floor, so they live here rather than inside any one level
 * editor — the content editor only assigns a piece of content to a chapter.
 */
export function ChapterEditorPage() {
  const { chapterId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const editingId = chapterId ? Number(chapterId) : null
  const isNew = editingId === null
  const presetChapterIndex = Number(searchParams.get('chapter'))
  const hasPresetChapterIndex = Number.isInteger(presetChapterIndex) && presetChapterIndex > 0
  const newChapterDraft = useMemo(
    () => blankChapter(hasPresetChapterIndex ? presetChapterIndex : 0),
    [hasPresetChapterIndex, presetChapterIndex],
  )

  const chaptersQuery = useQuery({
    queryKey: queryKeys.authoringChapters,
    queryFn: authoringApi.chapters,
    enabled: !isNew,
  })
  const loaded = chaptersQuery.data?.results.find((chapter) => chapter.id === editingId) ?? null

  const [draftOverride, setDraftOverride] = useState<AuthoringChapter | null>(null)
  const [savedSnapshot, setSavedSnapshot] = useState<AuthoringChapter | null>(null)
  const draft = draftOverride ?? (isNew ? newChapterDraft : loaded)

  const save = useMutation({
    mutationFn: () => {
      if (!draft) throw new Error('Chapter not loaded.')
      const input = {
        title: draft.title.trim(),
        summary: draft.summary?.trim() ?? '',
        ...(isNew && hasPresetChapterIndex ? { sort_order: draft.sort_order } : {}),
      }
      return isNew ? authoringApi.createChapter(input) : authoringApi.updateChapter(editingId as number, input)
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringChapters })
      setSavedSnapshot(saved)
      toast.success(isNew ? 'Chapter created.' : 'Chapter saved.')
      navigate('/level-editor')
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Could not save the chapter.')
    },
  })

  const baseline = savedSnapshot ?? loaded ?? (isNew ? newChapterDraft : null)
  const isDirty = Boolean(draft && baseline && !sameChapter(draft, baseline))
  useUnsavedChangesGuard({ when: isDirty && !save.isPending })

  if (!isNew && chaptersQuery.isLoading) return <LoadingState label="Loading chapter" variant="page" />
  if (!isNew && chaptersQuery.isError)
    return <ErrorState title="Could not load chapter" description={chaptersQuery.error.message} />
  if (!isNew && !loaded) return <ErrorState title="Chapter not found" description="It may have been deleted." />
  if (!draft) return <LoadingState label="Loading chapter" variant="page" />

  return (
    <div className="author-page">
      <header className="author-page-head">
        <div>
          <p className="author-eyebrow">Content Manager · chapter</p>
          <h1 className="author-page-title">{isNew ? 'Create chapter' : draft.title || 'Chapter'}</h1>
        </div>
        <div className="author-actions">
          <span className="author-save-status" data-state={save.isPending ? 'saving' : isDirty ? 'dirty' : 'saved'} aria-live="polite">
            {save.isPending ? 'Saving…' : isDirty ? 'Unsaved changes' : 'Saved'}
          </span>
          <Button variant="outline" size="sm" onClick={() => navigate('/level-editor')}>
            <ArrowLeft className="size-4" aria-hidden="true" /> Back
          </Button>
          <Button size="sm" disabled={!draft.title.trim() || save.isPending} onClick={() => save.mutate()}>
            <Save className="size-4" aria-hidden="true" />
            {save.isPending ? 'Saving…' : isNew ? 'Create chapter' : 'Save chapter'}
          </Button>
        </div>
      </header>

      <p className="author-hint author-page-lead">
        <Layers className="size-4" aria-hidden="true" />
        These settings are shared by every adventure, challenge, and lesson in this chapter.
      </p>

      <ChapterSettingsCard chapter={draft} onChange={(patch) => setDraftOverride({ ...draft, ...patch })} />

      {save.isError ? (
        <p role="alert" className="editor-warning is-error">
          {save.error instanceof Error ? save.error.message : 'Could not save the chapter.'}
        </p>
      ) : null}
    </div>
  )
}
