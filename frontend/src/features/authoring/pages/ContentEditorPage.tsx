import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Code2, Ghost, Layers, Plus, Rocket, Save } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'

import { authoringApi, type ContentDefinitionInput } from '@/features/authoring/api/authoringApi'
import {
  definitionErrorMessage,
  formFromContent,
  formToDefinition,
  initialForm,
  type AuthoringForm,
} from '@/features/authoring/authoringModel'
import { LevelsEditor } from '@/features/authoring/components/LevelsEditor'
import { MonsterUploadDialog } from '@/features/authoring/components/MonsterUploadDialog'
import { StoreySettingsCard } from '@/features/authoring/components/StoreySettingsCard'
import { TomePagesEditor } from '@/features/authoring/components/TomePagesEditor'
import type { AuthoringStorey, ContentKind } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type DraftState = { sourceKey: string; form: AuthoringForm }

export function ContentEditorPage() {
  const { definitionId, kind } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const parsedId = definitionId ? Number(definitionId) : null
  const newKind = (kind || 'adventure') as ContentKind
  const isNew = parsedId === null
  const [formError, setFormError] = useState<string | null>(null)
  const [showRaw, setShowRaw] = useState(false)
  const [monsterOpen, setMonsterOpen] = useState(false)
  // Local, unsaved edits to the selected storey's settings.
  const [storeyEdit, setStoreyEdit] = useState<AuthoringStorey | null>(null)

  const [searchParams] = useSearchParams()
  const presetStoreyId = searchParams.get('storey') ? Number(searchParams.get('storey')) : null

  const initialSourceKey = `new:${newKind}`
  const [draft, setDraft] = useState<DraftState>(() => ({
    sourceKey: initialSourceKey,
    form: { ...initialForm(newKind), storeyId: presetStoreyId },
  }))

  const detail = useQuery({
    queryKey: parsedId ? queryKeys.authoringContentDetail(parsedId) : ['authoring-content-new', newKind],
    queryFn: () => authoringApi.get(parsedId as number),
    enabled: parsedId !== null,
  })
  const storeysQuery = useQuery({ queryKey: queryKeys.authoringStoreys, queryFn: authoringApi.storeys })
  const storeys = useMemo(() => storeysQuery.data?.results ?? [], [storeysQuery.data])

  const loadedForm = useMemo(() => (detail.data ? formFromContent(detail.data) : null), [detail.data])
  const sourceKey = detail.data ? `content:${detail.data.id}` : initialSourceKey
  const form = draft.sourceKey === sourceKey ? draft.form : loadedForm ?? initialForm(newKind)

  // Keep the storey-settings draft in sync with the selected storey.
  useEffect(() => {
    const selected = storeys.find((s) => s.id === form.storeyId) ?? null
    setStoreyEdit((prev) => (prev && prev.id === selected?.id ? prev : selected))
  }, [form.storeyId, storeys])

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
      storey: form.storeyId,
      definition,
    }
  }

  const createStorey = useMutation({
    mutationFn: () => authoringApi.createStorey({ title: `Storey ${storeys.length + 1}` }),
    onSuccess: (storey) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringStoreys })
      setForm({ ...form, storeyId: storey.id })
      setStoreyEdit(storey)
    },
    onError: (error) =>
      setFormError(definitionErrorMessage(error) ?? (error instanceof Error ? error.message : 'Could not create storey.')),
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      // Persist storey-setting edits first so the content's storey is current.
      if (storeyEdit) {
        await authoringApi.updateStorey(storeyEdit.id, {
          title: storeyEdit.title,
          mob_roster: storeyEdit.mob_roster,
          boss_roster: storeyEdit.boss_roster,
          pass_bar_fraction: storeyEdit.pass_bar_fraction,
        })
      }
      const input = buildInput()
      return isNew ? authoringApi.create(input) : authoringApi.update(parsedId as number, input)
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringStoreys })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(saved.id) })
      if (isNew) navigate(`/authoring/${saved.id}`, { replace: true })
    },
    onError: (error) => setFormError(definitionErrorMessage(error) ?? (error instanceof Error ? error.message : 'Could not save.')),
  })
  const validateMutation = useMutation({
    mutationFn: () => authoringApi.validate(parsedId as number),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(parsedId as number) }),
  })
  const publishMutation = useMutation({
    mutationFn: () => authoringApi.publish(parsedId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(parsedId as number) })
    },
  })

  const canUseActions = !isNew && parsedId !== null
  const busy = saveMutation.isPending || validateMutation.isPending || publishMutation.isPending
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
      {monsterOpen ? <MonsterUploadDialog onClose={() => setMonsterOpen(false)} /> : null}

      <header className="author-page-head">
        <div>
          <p className="author-eyebrow">The Scriptorium · {form.kind}</p>
          <h1 className="author-page-title">{isNew ? `New ${form.kind}` : form.title}</h1>
        </div>
        <div className="author-actions">
          {form.kind !== 'tome' ? (
            <Button variant="outline" size="sm" onClick={() => setMonsterOpen(true)}>
              <Ghost className="size-4" aria-hidden="true" /> Upload monster
            </Button>
          ) : null}
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
            <Layers className="size-4" aria-hidden="true" /> Storey
          </h2>
          <p className="author-card-sub">Which floor of your tower this belongs to. A storey holds one adventure and many challenges/tomes.</p>
        </header>
        <div className="author-inline-row">
          <select
            className="author-input"
            value={form.storeyId ?? ''}
            onChange={(e) => setForm({ ...form, storeyId: e.target.value ? Number(e.target.value) : null })}
          >
            <option value="">— Unassigned —</option>
            {storeys.map((storey) => (
              <option key={storey.id} value={storey.id}>
                {storey.title}
              </option>
            ))}
          </select>
          <Button variant="outline" size="sm" disabled={createStorey.isPending} onClick={() => createStorey.mutate()}>
            <Plus className="size-4" aria-hidden="true" /> New storey
          </Button>
        </div>
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
        {form.kind !== 'tome' ? (
          <label className="author-field">
            <span className="author-label">Command family</span>
            <input className="author-input" value={form.commandFamily} onChange={(e) => setForm({ ...form, commandFamily: e.target.value })} placeholder="git status" />
          </label>
        ) : null}
      </section>

      {storeyEdit ? (
        <StoreySettingsCard
          kind={form.kind}
          storey={storeyEdit}
          onChange={(patch) => setStoreyEdit({ ...storeyEdit, ...patch })}
        />
      ) : (
        <p className="author-hint author-storey-empty">Assign or create a storey to set reward checkpoints and monster rosters.</p>
      )}

      {form.kind === 'tome' ? (
        <TomePagesEditor pages={form.pages} onChange={(pages) => setForm({ ...form, pages })} />
      ) : (
        <LevelsEditor kind={form.kind} levels={form.levels} onChange={(levels) => setForm({ ...form, levels })} />
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
        <button type="button" className="author-raw-toggle" onClick={() => setShowRaw((v) => !v)}>
          <Code2 className="size-4" aria-hidden="true" /> {showRaw ? 'Hide' : 'Show'} the generated JSON
        </button>
        {showRaw ? <pre className="author-raw">{rawJson}</pre> : null}
      </section>
    </div>
  )
}

export default ContentEditorPage
