import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpen, CheckCircle2, Layers, Pencil, Play, Plus, Rocket, Swords, Trophy } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import type { AuthoringStorey, ContentDefinition, ContentKind } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

const KIND_META: Record<ContentKind, { label: string; icon: typeof Swords }> = {
  adventure: { label: 'Adventure', icon: Swords },
  challenge: { label: 'Challenge', icon: Trophy },
  tome: { label: 'Tome', icon: BookOpen },
}
const KIND_ORDER: ContentKind[] = ['adventure', 'challenge', 'tome']

export function AuthoringLibraryPage() {
  const queryClient = useQueryClient()
  const contentQuery = useQuery({
    queryKey: queryKeys.authoringContent(),
    queryFn: () => authoringApi.list(),
    staleTime: 60 * 1000,
  })
  const storeysQuery = useQuery({ queryKey: queryKeys.authoringStoreys, queryFn: authoringApi.storeys })

  const createStorey = useMutation({
    mutationFn: () => authoringApi.createStorey({ title: `Storey ${(storeysQuery.data?.results.length ?? 0) + 1}` }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.authoringStoreys }),
  })

  if (contentQuery.isLoading || storeysQuery.isLoading)
    return <LoadingState label="Opening the Scriptorium" variant="page" />
  if (contentQuery.isError)
    return <ErrorState title="Could not open the Scriptorium" description={contentQuery.error.message} />

  const all = contentQuery.data?.results ?? []
  const storeys = storeysQuery.data?.results ?? []
  const unassigned = all.filter((c) => c.storey_id == null)

  return (
    <div className="scriptorium">
      <header className="scriptorium-head">
        <p className="editor-eyebrow">The Scriptorium</p>
        <h1 className="scriptorium-title">Author your lore</h1>
        <p className="scriptorium-sub">
          A storey is a floor of your tower — it holds one adventure plus its challenges and tomes. Author content into a
          storey, then publish to bind it onto your tower.
        </p>
        <Button size="sm" variant="outline" disabled={createStorey.isPending} onClick={() => createStorey.mutate()}>
          <Plus className="size-4" aria-hidden="true" /> New storey
        </Button>
        {createStorey.isError ? (
          <p className="editor-warning is-error">
            {createStorey.error instanceof Error ? createStorey.error.message : 'Could not create storey.'}
          </p>
        ) : null}
      </header>

      {storeys.map((storey) => (
        <StoreyGroup key={storey.id} storey={storey} content={all.filter((c) => c.storey_id === storey.id)} />
      ))}

      <StoreyGroup storey={null} content={unassigned} />
    </div>
  )
}

function StoreyGroup({ storey, content }: { storey: AuthoringStorey | null; content: ContentDefinition[] }) {
  const storeyId = storey?.id ?? null
  if (storey === null && content.length === 0) return null

  return (
    <section className="scriptorium-group">
      <div className="scriptorium-group-head">
        <h2 className="scriptorium-group-title">
          <Layers className="size-4" aria-hidden="true" />
          {storey ? storey.title : 'Unassigned'}
        </h2>
        <div className="scriptorium-new-row">
          {KIND_ORDER.map((kind) => (
            <Link
              key={kind}
              className="scriptorium-new"
              to={storeyId ? `/authoring/new/${kind}?storey=${storeyId}` : `/authoring/new/${kind}`}
            >
              <Plus className="size-3.5" aria-hidden="true" />
              {KIND_META[kind].label}
            </Link>
          ))}
        </div>
      </div>

      {content.length === 0 ? (
        <p className="scriptorium-empty">No content in this storey yet.</p>
      ) : (
        <ul className="scriptorium-list">
          {content
            .slice()
            .sort((a, b) => KIND_ORDER.indexOf(a.kind) - KIND_ORDER.indexOf(b.kind))
            .map((row) => (
              <ContentRow key={row.id} content={row} />
            ))}
        </ul>
      )}
    </section>
  )
}

function ContentRow({ content }: { content: ContentDefinition }) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const KindIcon = KIND_META[content.kind].icon

  function invalidate() {
    queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
    queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(content.id) })
  }

  const validate = useMutation({ mutationFn: () => authoringApi.validate(content.id), onSuccess: invalidate })
  const publish = useMutation({ mutationFn: () => authoringApi.publish(content.id), onSuccess: invalidate })
  const testRun = useMutation({
    mutationFn: () => authoringApi.testRun(content.id),
    onSuccess: (result) => {
      if (result.start_path) navigate(result.start_path)
    },
  })
  const busy = validate.isPending || publish.isPending || testRun.isPending

  return (
    <li className="scriptorium-row">
      <Link to={`/authoring/${content.id}`} className="scriptorium-row-main">
        <KindIcon className="size-3.5" aria-hidden="true" />
        <span className="scriptorium-row-title">{content.title}</span>
        <span className={cn('scriptorium-status', `is-${content.status}`)}>{content.status}</span>
      </Link>
      <div className="scriptorium-row-actions">
        <button type="button" className="scriptorium-action" disabled={busy} onClick={() => validate.mutate()}>
          <CheckCircle2 className="size-3.5" aria-hidden="true" />
          Validate
        </button>
        <button
          type="button"
          className="scriptorium-action"
          disabled={busy || content.status === 'draft'}
          onClick={() => testRun.mutate()}
          title={content.status === 'draft' ? 'Validate first to test-play' : undefined}
        >
          <Play className="size-3.5" aria-hidden="true" />
          Test-play
        </button>
        <button type="button" className="scriptorium-action" disabled={busy} onClick={() => publish.mutate()}>
          <Rocket className="size-3.5" aria-hidden="true" />
          Publish
        </button>
        <Link to={`/authoring/${content.id}`} className="scriptorium-action" aria-label="Edit">
          <Pencil className="size-3.5" aria-hidden="true" />
        </Link>
      </div>
    </li>
  )
}

export default AuthoringLibraryPage
