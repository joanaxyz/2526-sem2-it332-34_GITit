import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, BookOpen, CheckCircle2, Layers, Pencil, Play, Plus, Rocket, Settings2, Swords, Trophy } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { authoringApi } from '@/features/authoring/api/authoringApi'
import type { AuthoringChapter, ContentDefinition, ContentKind, ContentStatus } from '@/features/authoring/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

const KIND_META: Record<ContentKind, { label: string; icon: typeof Swords }> = {
  adventure: { label: 'Adventure', icon: Swords },
  challenge: { label: 'Challenge', icon: Trophy },
  lesson: { label: 'ChapterLesson', icon: BookOpen },
}
const KIND_ORDER: ContentKind[] = ['adventure', 'challenge', 'lesson']
const STATUS_LABELS: Record<ContentStatus, string> = {
  draft: 'Draft',
  testable: 'Tested',
  published: 'Published',
  archived: 'Archived',
}

export function AuthoringLibraryPage() {
  const contentQuery = useQuery({
    queryKey: queryKeys.authoringContent(),
    queryFn: () => authoringApi.list(),
    staleTime: 60 * 1000,
  })
  const chaptersQuery = useQuery({ queryKey: queryKeys.authoringChapters, queryFn: authoringApi.chapters })

  if (contentQuery.isLoading || chaptersQuery.isLoading)
    return <LoadingState label="Opening content library" variant="page" />
  if (contentQuery.isError)
    return <ErrorState title="Could not open content library" description={contentQuery.error.message} />

  const all = contentQuery.data?.results ?? []
  const chapters = chaptersQuery.data?.results ?? []
  const unassigned = all.filter((c) => c.chapter_id == null)

  return (
    <div className="scriptorium">
      <header className="scriptorium-head">
        <p className="editor-eyebrow">Content Library</p>
        <h1 className="scriptorium-title">Manage content</h1>
        <p className="scriptorium-sub">
          A chapter holds one adventure plus its challenges and lessons. Author content into a chapter, then publish it
          onto the curriculum map.
        </p>
        <Button asChild size="sm" variant="outline">
          <Link to="/level-editor/chapters/new">
            <Plus className="size-4" aria-hidden="true" /> New chapter
          </Link>
        </Button>
      </header>

      {chapters.map((chapter) => (
        <ChapterGroup key={chapter.id} chapter={chapter} content={all.filter((c) => c.chapter_id === chapter.id)} />
      ))}

      <ChapterGroup chapter={null} content={unassigned} />
    </div>
  )
}

function ChapterGroup({ chapter, content }: { chapter: AuthoringChapter | null; content: ContentDefinition[] }) {
  const chapterId = chapter?.id ?? null
  if (chapter === null && content.length === 0) return null

  return (
    <section className="scriptorium-group">
      <div className="scriptorium-group-head">
        <h2 className="scriptorium-group-title">
          <Layers className="size-4" aria-hidden="true" />
          {chapter ? chapter.title : 'Unassigned'}
        </h2>
        <div className="scriptorium-new-row">
          {chapter ? (
            <Link className="scriptorium-new" to={`/level-editor/chapters/${chapter.id}`}>
              <Settings2 className="size-3.5" aria-hidden="true" />
              Edit chapter
            </Link>
          ) : null}
          {KIND_ORDER.map((kind) => (
            <Link
              key={kind}
              className="scriptorium-new"
              to={chapterId ? `/level-editor/new/${kind}?chapter=${chapterId}` : `/level-editor/new/${kind}`}
            >
              <Plus className="size-3.5" aria-hidden="true" />
              {KIND_META[kind].label}
            </Link>
          ))}
        </div>
      </div>

      {content.length === 0 ? (
        <p className="scriptorium-empty">No content in this chapter yet.</p>
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

  const validate = useMutation({
    mutationFn: () => authoringApi.validate(content.id),
    onSuccess: (result) => {
      invalidate()
      if (result.valid) {
        toast.success(`${content.title} is ready to test.`)
      } else {
        toast.error(`${content.title} has ${result.errors.length} validation issue${result.errors.length === 1 ? '' : 's'}.`)
      }
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Could not validate this content.')
    },
  })
  const publish = useMutation({
    mutationFn: () => authoringApi.publish(content.id),
    onSuccess: () => {
      invalidate()
      toast.success(`${content.title} published.`)
    },
    onError: (error) => {
      toast.error(error instanceof Error ? error.message : 'Could not publish this content.')
    },
  })
  const testRun = useMutation({
    mutationFn: () => authoringApi.testRun(content.id),
    onSuccess: (result) => {
      if (result.start_path) navigate(result.start_path)
    },
  })
  const busy = validate.isPending || publish.isPending || testRun.isPending

  return (
    <li className="scriptorium-row">
      <div className="scriptorium-row-content">
        <Link to={`/level-editor/${content.id}`} className="scriptorium-row-main">
          <KindIcon className="size-3.5" aria-hidden="true" />
          <span className="scriptorium-row-title">{content.title}</span>
          <span className={cn('scriptorium-status', `is-${content.status}`)}>
            {STATUS_LABELS[content.status]}
          </span>
        </Link>
        {content.validation_errors.length ? (
          <ul className="scriptorium-row-errors" aria-label={`${content.title} validation errors`}>
            {content.validation_errors.slice(0, 3).map((error) => (
              <li key={`${error.field}-${error.message}`}>
                <AlertCircle className="size-3.5" aria-hidden="true" />
                <span>
                  {error.field}: {error.message}
                </span>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
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
        <Link to={`/level-editor/${content.id}`} className="scriptorium-action" aria-label="Edit">
          <Pencil className="size-3.5" aria-hidden="true" />
        </Link>
      </div>
    </li>
  )
}

export default AuthoringLibraryPage
