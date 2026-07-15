import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Code2, Layers, Plus, Rocket, Save, Settings2 } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { authoringApi, type ContentDefinitionInput } from '@/features/authoring/api/authoringApi'
import {
  compileSummary,
  definitionErrorMessage,
  DIFFICULTIES,
  formFromContent,
  formToDefinition,
  initialForm,
  VISIBILITIES,
  type AuthoringForm,
} from '@/features/authoring/utils/authoringModel'
import { BattleStageEditor } from '@/features/authoring/components/BattleStageEditor'
import { LevelsEditor } from '@/features/authoring/components/LevelsEditor'
import { ChapterLessonPagesEditor } from '@/features/authoring/components/ChapterLessonPagesEditor'
import { useUnsavedChangesGuard } from '@/features/authoring/hooks/useUnsavedChangesGuard'
import type { ContentKind } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type DraftState = { sourceKey: string; form: AuthoringForm }

function sameForm(a: AuthoringForm, b: AuthoringForm): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

export function ContentEditorPage() {
  const { definitionId, kind } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const parsedId = definitionId ? Number(definitionId) : null
  const newKind = (kind || 'adventure') as ContentKind
  const isNew = parsedId === null
  const [formError, setFormError] = useState<string | null>(null)
  const [showRaw, setShowRaw] = useState(false)
  const [savedSnapshot, setSavedSnapshot] = useState<DraftState | null>(null)

  const [searchParams] = useSearchParams()
  const presetChapterId = searchParams.get('chapter') ? Number(searchParams.get('chapter')) : null

  const initialSourceKey = `new:${newKind}`
  const [draft, setDraft] = useState<DraftState>(() => ({
    sourceKey: initialSourceKey,
    form: { ...initialForm(newKind), chapterId: presetChapterId },
  }))

  const detail = useQuery({
    queryKey: parsedId ? queryKeys.authoringContentDetail(parsedId) : ['authoring-content-new', newKind],
    queryFn: () => authoringApi.get(parsedId as number),
    enabled: parsedId !== null,
  })
  const chaptersQuery = useQuery({ queryKey: queryKeys.authoringChapters, queryFn: authoringApi.chapters })
  const commandFormsQuery = useQuery({
    queryKey: ['authoring-command-forms'],
    queryFn: authoringApi.commandForms,
    staleTime: 5 * 60 * 1000,
    enabled: newKind !== 'lesson',
  })
  const chapters = useMemo(() => chaptersQuery.data?.results ?? [], [chaptersQuery.data])

  const loadedForm = useMemo(() => (detail.data ? formFromContent(detail.data) : null), [detail.data])
  const sourceKey = detail.data ? `content:${detail.data.id}` : initialSourceKey
  const initialNewForm = useMemo(
    () => ({ ...initialForm(newKind), chapterId: presetChapterId }),
    [newKind, presetChapterId],
  )
  const form = draft.sourceKey === sourceKey ? draft.form : loadedForm ?? initialNewForm
  const baselineForm = savedSnapshot?.sourceKey === sourceKey ? savedSnapshot.form : loadedForm ?? initialNewForm
  const isDirty = !sameForm(form, baselineForm)

  function setForm(next: AuthoringForm) {
    setDraft({ sourceKey, form: next })
  }

  function buildInput(): ContentDefinitionInput {
    setFormError(null)
    const definition = formToDefinition(form) // may throw on bad JSON
    return {
      kind: form.kind,
      slug: form.slug,
      title: form.title,
      summary: form.summary,
      command_family: form.commandFamily,
      difficulty: form.difficulty,
      tags: form.tags,
      visibility: form.visibility,
      chapter: form.chapterId,
      definition,
    }
  }

  const createChapter = useMutation({
    mutationFn: () => authoringApi.createChapter({ title: `Chapter ${chapters.length + 1}` }),
    onSuccess: (chapter) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringChapters })
      setForm({ ...form, chapterId: chapter.id })
    },
    onError: (error) =>
      setFormError(definitionErrorMessage(error) ?? (error instanceof Error ? error.message : 'Could not create chapter.')),
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      const input = buildInput()
      return isNew ? authoringApi.create(input) : authoringApi.update(parsedId as number, input)
    },
    onSuccess: (saved) => {
      const savedState = { sourceKey: `content:${saved.id}`, form: formFromContent(saved) }
      setSavedSnapshot(savedState)
      setDraft(savedState)
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringChapters })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(saved.id) })
      toast.success('Draft saved.')
      if (isNew) navigate(`/level-editor/${saved.id}`, { replace: true })
    },
    onError: (error) => {
      const message = definitionErrorMessage(error) ?? (error instanceof Error ? error.message : 'Could not save.')
      setFormError(message)
      toast.error(message)
    },
  })
  const validateMutation = useMutation({
    mutationFn: () => authoringApi.validate(parsedId as number),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(parsedId as number) })
      if (result.valid) {
        toast.success('Validation passed.')
      } else {
        toast.error(`${result.errors.length} validation issue${result.errors.length === 1 ? '' : 's'} found.`)
      }
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : 'Could not validate.'
      setFormError(message)
      toast.error(message)
    },
  })
  const publishMutation = useMutation({
    mutationFn: () => authoringApi.publish(parsedId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(parsedId as number) })
      toast.success('Published.')
    },
    onError: (error) => {
      const message = error instanceof Error ? error.message : 'Could not publish.'
      setFormError(message)
      toast.error(message)
    },
  })

  const canUseActions = !isNew && parsedId !== null
  const busy = saveMutation.isPending || validateMutation.isPending || publishMutation.isPending
  useUnsavedChangesGuard({ when: isDirty && !busy })
  const validationErrors = useMemo(() => detail.data?.validation_errors ?? [], [detail.data?.validation_errors])
  const rawJson = useMemo(() => {
    try {
      return JSON.stringify(formToDefinition(form), null, 2)
    } catch (error) {
      return definitionErrorMessage(error) ?? 'Definition is not yet valid.'
    }
  }, [form])

  if (detail.isLoading) return <LoadingState label="Loading content" variant="page" />
  if (detail.isError) return <ErrorState title="Could not load content" description={detail.error.message} />

  return (
    <div className="author-page">
      <header className="author-page-head">
        <div>
          <p className="author-eyebrow">Content Manager · {form.kind}</p>
          <h1 className="author-page-title">{isNew ? `New ${form.kind}` : form.title}</h1>
        </div>
        <div className="author-actions">
          <span className="author-save-status" data-state={busy ? 'saving' : isDirty ? 'dirty' : 'saved'} aria-live="polite">
            {busy ? 'Working…' : isDirty ? 'Unsaved changes' : 'Saved'}
          </span>
          <Button disabled={busy} size="sm" onClick={() => saveMutation.mutate()}>
            <Save className="size-4" aria-hidden="true" /> Save
          </Button>
          <Button disabled={!canUseActions || busy} variant="outline" size="sm" onClick={() => validateMutation.mutate()}>
            <CheckCircle2 className="size-4" aria-hidden="true" /> Validate
          </Button>
          <Button disabled={!canUseActions || busy} variant="secondary" size="sm" onClick={() => publishMutation.mutate()}>
            <Rocket className="size-4" aria-hidden="true" /> Publish
          </Button>
        </div>
      </header>

      <section className="author-card">
        <header className="author-card-head">
          <h2 className="author-card-title">
            <Layers className="size-4" aria-hidden="true" /> Chapter
          </h2>
          <p className="author-card-sub">Which chapter this belongs to. A chapter can hold adventures, challenges, and lessons.</p>
        </header>
        <div className="author-inline-row">
          <select
            className="author-input"
            value={form.chapterId ?? ''}
            onChange={(e) => setForm({ ...form, chapterId: e.target.value ? Number(e.target.value) : null })}
          >
            <option value="">— Unassigned —</option>
            {chapters.map((chapter) => (
              <option key={chapter.id} value={chapter.id}>
                {chapter.title}
              </option>
            ))}
          </select>
          <Button variant="outline" size="sm" disabled={createChapter.isPending} onClick={() => createChapter.mutate()}>
            <Plus className="size-4" aria-hidden="true" /> New chapter
          </Button>
          {form.chapterId ? (
            <Button asChild variant="outline" size="sm">
              <Link to={`/level-editor/chapters/${form.chapterId}`}>
                <Settings2 className="size-4" aria-hidden="true" /> Edit chapter
              </Link>
            </Button>
          ) : null}
        </div>
        <p className="author-hint">Name, overview, and challenge unlock settings live on the chapter's own page.</p>
      </section>

      <section className="author-card">
        <div className="author-grid-2">
          <label className="author-field">
            <span className="author-label">Title</span>
            <input className="author-input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </label>
          <label className="author-field">
            <span className="author-label">Slug</span>
            <input className="author-input" value={form.slug} onChange={(e) => setForm({ ...form, slug: e.target.value })} />
          </label>
        </div>
        <label className="author-field">
          <span className="author-label">Summary</span>
          <textarea className="author-input" rows={2} value={form.summary} onChange={(e) => setForm({ ...form, summary: e.target.value })} />
        </label>
        {form.kind !== 'lesson' ? (
          <div className="author-grid-2">
            <label className="author-field">
              <span className="author-label">Command family</span>
              <input className="author-input" value={form.commandFamily} onChange={(e) => setForm({ ...form, commandFamily: e.target.value })} placeholder="git status" />
            </label>
            <label className="author-field">
              <span className="author-label">Difficulty</span>
              <select
                className="author-input"
                value={form.difficulty}
                onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
              >
                {DIFFICULTIES.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
        ) : null}
        <div className="author-grid-2">
          <TagsField key={sourceKey} value={form.tags} onChange={(tags) => setForm({ ...form, tags })} />
          <label className="author-field">
            <span className="author-label">Visibility</span>
            <select
              className="author-input"
              value={form.visibility}
              onChange={(e) => setForm({ ...form, visibility: e.target.value as AuthoringForm['visibility'] })}
            >
              {VISIBILITIES.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {form.kind !== 'lesson' ? (
        <BattleStageEditor
          value={form.battleStage}
          onChange={(battleStage) => setForm({ ...form, battleStage })}
        />
      ) : null}

      {form.kind === 'lesson' ? (
        <ChapterLessonPagesEditor pages={form.pages} onChange={(pages) => setForm({ ...form, pages })} />
      ) : (
        <LevelsEditor
          kind={form.kind}
          levels={form.levels}
          onChange={(levels) => setForm({ ...form, levels })}
          commandFormOptions={commandFormsQuery.data?.results ?? []}
        />
      )}

      {formError ? <p className="editor-warning is-error">{formError}</p> : null}
      {validationErrors.length ? (
        <ul className="author-errors">
          {validationErrors.map((error) => (
            <li key={`${error.field}-${error.message}`}>
              {error.field}: {error.message}
            </li>
          ))}
        </ul>
      ) : null}

      <section className="author-card">
        <p className="author-hint">Compiles to {compileSummary(form)}.</p>
        <button type="button" className="author-raw-toggle" onClick={() => setShowRaw((v) => !v)}>
          <Code2 className="size-4" aria-hidden="true" /> {showRaw ? 'Hide' : 'Show'} the generated JSON
        </button>
        {showRaw ? <pre className="author-raw">{rawJson}</pre> : null}
      </section>
    </div>
  )
}

/** Comma-separated tag input that keeps the raw text the author is typing
 *  (so a trailing comma survives) while exposing a cleaned string[] upstream. */
function TagsField({ value, onChange }: { value: string[]; onChange: (tags: string[]) => void }) {
  const [text, setText] = useState(() => value.join(', '))
  return (
    <label className="author-field">
      <span className="author-label">Tags</span>
      <span className="author-hint">Comma-separated, used for search and the store.</span>
      <input
        className="author-input"
        value={text}
        onChange={(e) => {
          setText(e.target.value)
          onChange(e.target.value.split(',').map((tag) => tag.trim()).filter(Boolean))
        }}
        placeholder="branching, merge"
      />
    </label>
  )
}

export default ContentEditorPage
