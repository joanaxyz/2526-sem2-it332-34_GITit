import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { adminApi, type AdminChapter, type AdminStory } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminCurriculumPage() {
  const queryClient = useQueryClient()
  const [openStory, setOpenStory] = useState<number | null>(null)

  const storiesQuery = useQuery({ queryKey: queryKeys.adminStories, queryFn: adminApi.stories })
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.adminStories })

  return (
    <div>
      <PageHeading
        title="Curriculum & Stories"
        description="Edit the curriculum stories players progress through. Chapter progress chests use a fixed, runtime-computed reward schedule — nothing to author here."
      />

      <CreateStory onCreated={invalidate} />

      {storiesQuery.isPending ? (
        <LoadingState label="Loading stories" variant="panel" />
      ) : storiesQuery.isError ? (
        <ErrorState title="Could not load curriculum" description="Try again shortly." />
      ) : (
        <div className="mt-4 grid gap-3">
          {storiesQuery.data.results.map((story) => (
            <StoryRow
              key={story.id}
              story={story}
              expanded={openStory === story.id}
              onToggle={() => setOpenStory((prev) => (prev === story.id ? null : story.id))}
              onChanged={invalidate}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function CreateStory({ onCreated }: { onCreated: () => void }) {
  const [slug, setSlug] = useState('')
  const [title, setTitle] = useState('')

  const create = useMutation({
    mutationFn: () => adminApi.createStory({ slug: slug.trim(), title: title.trim() }),
    onSuccess: () => {
      setSlug('')
      setTitle('')
      onCreated()
    },
  })

  return (
    <form
      className="flex flex-wrap items-end gap-2 rounded-lg border border-border bg-card p-3"
      onSubmit={(e) => {
        e.preventDefault()
        if (slug.trim() && title.trim()) create.mutate()
      }}
    >
      <input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="slug" className="h-9 w-40 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50" />
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" className="h-9 flex-1 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50" />
      <Button type="submit" size="sm" disabled={create.isPending}>Add story</Button>
    </form>
  )
}

function StoryRow({ story, expanded, onToggle, onChanged }: { story: AdminStory; expanded: boolean; onToggle: () => void; onChanged: () => void }) {
  const update = useMutation({
    mutationFn: (patch: Parameters<typeof adminApi.updateStory>[1]) => adminApi.updateStory(story.id, patch),
    onSuccess: onChanged,
  })

  return (
    <div className="rounded-lg border border-border bg-card">
      <div className="flex items-center gap-3 p-3">
        <button onClick={onToggle} className="flex-1 text-left">
          <p className="font-semibold text-foreground">{story.title}</p>
          <p className="text-xs text-muted-foreground">{story.slug} · {story.chapter_count} chapters</p>
        </button>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" disabled={update.isPending} onClick={() => update.mutate({ is_published: !story.is_published })}>
            {story.is_published ? 'Published' : 'Draft'}
          </Button>
        </div>
      </div>
      {expanded ? <ChapterList storyId={story.id} /> : null}
    </div>
  )
}

function ChapterList({ storyId }: { storyId: number }) {
  const chaptersQuery = useQuery({
    queryKey: queryKeys.adminChapters(storyId),
    queryFn: () => adminApi.chapters(storyId),
  })

  if (chaptersQuery.isPending) return <LoadingState label="Loading chapters" variant="inline" />
  if (chaptersQuery.isError || !chaptersQuery.data)
    return <p className="px-3 pb-3 text-xs text-destructive">Could not load chapters.</p>

  return (
    <div className="border-t border-border/60 p-3">
      {chaptersQuery.data.results.length === 0 ? (
        <p className="text-xs text-muted-foreground">No chapters in this story.</p>
      ) : (
        <div className="grid gap-2">
          {chaptersQuery.data.results.map((chapter) => (
            <ChapterRow key={chapter.id} chapter={chapter} storyId={storyId} />
          ))}
        </div>
      )}
    </div>
  )
}

function ChapterRow({ chapter, storyId }: { chapter: AdminChapter; storyId: number }) {
  const queryClient = useQueryClient()

  const update = useMutation({
    mutationFn: (patch: Parameters<typeof adminApi.updateChapter>[1]) => adminApi.updateChapter(chapter.id, patch),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.adminChapters(storyId) })
    },
  })

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-md bg-background/40 px-3 py-2">
      <span className="text-sm font-medium text-foreground">#{chapter.number} {chapter.title}</span>
      <Button
        size="sm"
        variant="outline"
        disabled={update.isPending}
        className="ml-auto"
        onClick={() => update.mutate({ is_published: !chapter.is_published })}
      >
        {chapter.is_published ? 'Published' : 'Draft'}
      </Button>
    </div>
  )
}
