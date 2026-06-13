import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, Rocket, Save } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { authoringApi, type ContentDefinitionInput } from '@/features/authoring/api/authoringApi'
import type { ContentKind } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/components/Card'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

type FormState = {
  kind: ContentKind
  slug: string
  title: string
  summary: string
  command_family: string
  difficulty: string
  definitionText: string
}

const starterDefinitions: Record<ContentKind, Record<string, unknown>> = {
  adventure: {
    levels: [
      {
        slug: 'status-check',
        title: 'Check status',
        initial_state: {},
        solution_commands: ['git status'],
        evaluation_spec: { completion_policy: { mode: 'state_hash' } },
      },
    ],
  },
  challenge: {
    levels: [
      {
        slug: 'status-check',
        title: 'Check status',
        difficulty: 'easy',
        initial_state: {},
        solution_commands: ['git status'],
        evaluation_spec: { completion_policy: { mode: 'state_hash' } },
      },
    ],
  },
  tome: {
    pages: [{ title: 'Overview', blocks: [{ type: 'paragraph', body: 'Draft your lesson here.' }] }],
  },
}

export function ContentEditorPage() {
  const { definitionId, kind } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const parsedId = definitionId ? Number(definitionId) : null
  const newKind = (kind || 'adventure') as ContentKind
  const isNew = parsedId === null
  const [jsonError, setJsonError] = useState<string | null>(null)
  const [form, setForm] = useState<FormState>(() => initialForm(newKind))

  const detail = useQuery({
    queryKey: parsedId ? queryKeys.authoringContentDetail(parsedId) : ['authoring-content-new', newKind],
    queryFn: () => authoringApi.get(parsedId as number),
    enabled: parsedId !== null,
  })

  useEffect(() => {
    if (!detail.data) return
    setForm({
      kind: detail.data.kind,
      slug: detail.data.slug,
      title: detail.data.title,
      summary: detail.data.summary,
      command_family: detail.data.command_family,
      difficulty: detail.data.difficulty,
      definitionText: JSON.stringify(detail.data.definition ?? {}, null, 2),
    })
  }, [detail.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const input = toInput(form)
      return isNew ? authoringApi.create(input) : authoringApi.update(parsedId as number, input)
    },
    onSuccess: (saved) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(saved.id) })
      if (isNew) navigate(`/authoring/${saved.id}`, { replace: true })
    },
    onError: (error) => setJsonError(error instanceof Error ? error.message : 'Could not save content.'),
  })
  const validateMutation = useMutation({
    mutationFn: () => authoringApi.validate(parsedId as number),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(parsedId as number) })
    },
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

  if (detail.isLoading) return <LoadingState label="Loading content" variant="page" />
  if (detail.isError) return <ErrorState title="Could not load content" description={detail.error.message} />

  function update(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function toInput(state: FormState): ContentDefinitionInput {
    setJsonError(null)
    try {
      return {
        kind: state.kind,
        slug: state.slug,
        title: state.title,
        summary: state.summary,
        command_family: state.command_family,
        difficulty: state.difficulty,
        definition: JSON.parse(state.definitionText) as Record<string, unknown>,
      }
    } catch {
      const message = 'Definition JSON is not valid.'
      setJsonError(message)
      throw new Error(message)
    }
  }

  return (
    <div className="grid gap-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">{form.kind}</p>
        <h1 className="mt-2 text-3xl font-black text-foreground">{isNew ? 'New content' : form.title}</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Definition</CardTitle>
          <CardDescription>Validated on the server before it can be test-played or published.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="grid gap-3 md:grid-cols-2">
            <input className="rounded-md border border-border bg-background/40 px-3 py-2" value={form.title} onChange={(event) => update('title', event.target.value)} placeholder="Title" />
            <input className="rounded-md border border-border bg-background/40 px-3 py-2" value={form.slug} onChange={(event) => update('slug', event.target.value)} placeholder="slug" />
            <input className="rounded-md border border-border bg-background/40 px-3 py-2" value={form.command_family} onChange={(event) => update('command_family', event.target.value)} placeholder="Command family" />
            <input className="rounded-md border border-border bg-background/40 px-3 py-2" value={form.difficulty} onChange={(event) => update('difficulty', event.target.value)} placeholder="Difficulty" />
          </div>
          <textarea className="min-h-20 rounded-md border border-border bg-background/40 px-3 py-2" value={form.summary} onChange={(event) => update('summary', event.target.value)} placeholder="Summary" />
          <textarea className="min-h-96 rounded-md border border-border bg-background/40 px-3 py-2 font-mono text-sm" value={form.definitionText} onChange={(event) => update('definitionText', event.target.value)} spellCheck={false} />
          {jsonError ? <p className="text-sm text-destructive">{jsonError}</p> : null}
          {validationErrors.length ? (
            <ul className="grid gap-2 text-sm text-destructive">
              {validationErrors.map((error) => (
                <li key={`${error.field}-${error.message}`}>{error.field}: {error.message}</li>
              ))}
            </ul>
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button disabled={busy} onClick={() => saveMutation.mutate()}>
              <Save className="size-4" />
              Save
            </Button>
            <Button disabled={!canUseActions || busy} variant="outline" onClick={() => validateMutation.mutate()}>
              <CheckCircle2 className="size-4" />
              Validate
            </Button>
            <Button disabled={!canUseActions || busy} variant="secondary" onClick={() => publishMutation.mutate()}>
              <Rocket className="size-4" />
              Publish
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function initialForm(kind: ContentKind): FormState {
  return {
    kind,
    slug: `new-${kind}`,
    title: `New ${kind}`,
    summary: '',
    command_family: kind === 'tome' ? '' : 'git status',
    difficulty: kind === 'challenge' ? 'easy' : '',
    definitionText: JSON.stringify(starterDefinitions[kind], null, 2),
  }
}

export default ContentEditorPage
