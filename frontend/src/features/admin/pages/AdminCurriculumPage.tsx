import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import {
  adminApi,
  type AdminStory,
  type AdminStoryCreatePayload,
} from '@/features/admin/api/adminApi'
import { AdminCurriculumChapters } from '@/features/admin/components/AdminCurriculumChapters'
import {
  CurriculumField as Field,
  CurriculumMutationMessage as MutationMessage,
  CurriculumStatusPill as StatusPill,
  fieldClass,
  textAreaClass,
} from '@/features/admin/components/AdminCurriculumUi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'

export function AdminCurriculumPage() {
  const queryClient = useQueryClient()
  const [openStory, setOpenStory] = useState<number | null>(null)
  const storiesQuery = useQuery({ queryKey: queryKeys.adminStories, queryFn: adminApi.stories })
  const invalidate = () => queryClient.invalidateQueries({ queryKey: queryKeys.adminStories })

  return (
    <div>
      <PageHeading
        title="Curriculum & Stories"
        description="Create draft campaigns, add their chapters, and publish them when they are ready. Saving a seeded row transfers that complete row to admin ownership."
      />

      {storiesQuery.isPending ? (
        <LoadingState label="Loading stories" variant="panel" />
      ) : storiesQuery.isError ? (
        <ErrorState title="Could not load curriculum" description="Try again shortly." />
      ) : (
        <>
          <CreateStory
            stories={storiesQuery.data.results}
            worldOptions={storiesQuery.data.world_options}
            onCreated={invalidate}
          />
          <div className="mt-4 grid gap-3">
            {storiesQuery.data.results.map((story) => (
              <StoryRow
                key={story.id}
                story={story}
                stories={storiesQuery.data.results}
                worldOptions={storiesQuery.data.world_options}
                expanded={openStory === story.id}
                onToggle={() => setOpenStory((previous) => (previous === story.id ? null : story.id))}
                onChanged={invalidate}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function CreateStory({
  stories,
  worldOptions,
  onCreated,
}: {
  stories: AdminStory[]
  worldOptions: string[]
  onCreated: () => void
}) {
  const [form, setForm] = useState<AdminStoryCreatePayload>({
    slug: '',
    title: '',
    summary: '',
    price: 0,
    world_slug: worldOptions[0] ?? 'arcane-spire',
    difficulty: 'beginner',
    prerequisite_story: null,
  })
  const create = useMutation({
    mutationFn: () => adminApi.createStory(form),
    onSuccess: () => {
      setForm({
        slug: '',
        title: '',
        summary: '',
        price: 0,
        world_slug: worldOptions[0] ?? 'arcane-spire',
        difficulty: 'beginner',
        prerequisite_story: null,
      })
      onCreated()
    },
  })

  return (
    <form
      className="grid gap-3 rounded-lg border border-border bg-card p-4"
      onSubmit={(event) => {
        event.preventDefault()
        if (form.slug.trim() && form.title.trim()) create.mutate()
      }}
    >
      <div>
        <h2 className="font-bold text-foreground">New story</h2>
        <p className="text-xs text-muted-foreground">New stories always start as drafts.</p>
      </div>
      <div className="grid gap-2 md:grid-cols-2">
        <Field label="Slug">
          <input
            required
            value={form.slug}
            onChange={(event) => setForm({ ...form, slug: event.target.value })}
            placeholder="story-slug"
            className={fieldClass}
          />
        </Field>
        <Field label="Title">
          <input
            required
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            placeholder="Story title"
            className={fieldClass}
          />
        </Field>
        <Field label="Visual world">
          <select
            value={form.world_slug}
            onChange={(event) => setForm({ ...form, world_slug: event.target.value })}
            className={fieldClass}
          >
            {worldOptions.map((slug) => <option key={slug}>{slug}</option>)}
          </select>
        </Field>
        <Field label="Difficulty">
          <select
            value={form.difficulty}
            onChange={(event) => setForm({ ...form, difficulty: event.target.value as AdminStory['difficulty'] })}
            className={fieldClass}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </Field>
        <Field label="Price">
          <input
            type="number"
            min={0}
            value={form.price}
            onChange={(event) => setForm({ ...form, price: Number(event.target.value) })}
            className={fieldClass}
          />
        </Field>
        <Field label="Prerequisite">
          <select
            value={form.prerequisite_story ?? ''}
            onChange={(event) => setForm({ ...form, prerequisite_story: event.target.value ? Number(event.target.value) : null })}
            className={fieldClass}
          >
            <option value="">None</option>
            {stories.map((story) => <option key={story.id} value={story.id}>{story.title}</option>)}
          </select>
        </Field>
      </div>
      <Field label="Summary">
        <textarea
          value={form.summary}
          onChange={(event) => setForm({ ...form, summary: event.target.value })}
          className={textAreaClass}
        />
      </Field>
      <MutationMessage mutation={create} />
      <Button type="submit" size="sm" className="w-fit" disabled={create.isPending}>
        {create.isPending ? 'Creating…' : 'Create draft story'}
      </Button>
    </form>
  )
}

function StoryRow({
  story,
  stories,
  worldOptions,
  expanded,
  onToggle,
  onChanged,
}: {
  story: AdminStory
  stories: AdminStory[]
  worldOptions: string[]
  expanded: boolean
  onToggle: () => void
  onChanged: () => void
}) {
  return (
    <section className="rounded-lg border border-border bg-card">
      <div className="flex items-center gap-3 p-3">
        <button type="button" onClick={onToggle} className="flex-1 text-left">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-foreground">{story.title}</p>
            <StatusPill active={story.is_published} />
            <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] uppercase text-muted-foreground">
              {story.management_source}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            {story.slug} · {story.world_slug} · {story.chapter_count} chapters
          </p>
        </button>
        <Button type="button" size="sm" variant="outline" onClick={onToggle}>
          {expanded ? 'Close' : 'Manage'}
        </Button>
      </div>
      {expanded ? (
        <div className="grid gap-4 border-t border-border/60 p-4">
          <StoryEditor
            story={story}
            stories={stories}
            worldOptions={worldOptions}
            onChanged={onChanged}
          />
          <AdminCurriculumChapters story={story} />
        </div>
      ) : null}
    </section>
  )
}

function StoryEditor({
  story,
  stories,
  worldOptions,
  onChanged,
}: {
  story: AdminStory
  stories: AdminStory[]
  worldOptions: string[]
  onChanged: () => void
}) {
  const [title, setTitle] = useState(story.title)
  const [summary, setSummary] = useState(story.summary)
  const [price, setPrice] = useState(story.price)
  const [worldSlug, setWorldSlug] = useState(story.world_slug)
  const [difficulty, setDifficulty] = useState(story.difficulty)
  const [prerequisite, setPrerequisite] = useState<number | null>(story.prerequisite_story?.id ?? null)
  const [sortOrder, setSortOrder] = useState(story.sort_order)
  const update = useMutation<AdminStory, Error, boolean>({
    mutationFn: (isPublished) => adminApi.updateStory(story.id, {
      title,
      summary,
      price,
      world_slug: worldSlug,
      difficulty,
      prerequisite_story: prerequisite,
      sort_order: sortOrder,
      is_published: isPublished,
    }),
    onSuccess: onChanged,
  })

  return (
    <div className="grid gap-3">
      <h3 className="text-sm font-bold text-foreground">Story details</h3>
      <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
        <Field label="Title"><input value={title} onChange={(event) => setTitle(event.target.value)} className={fieldClass} /></Field>
        <Field label="Visual world">
          <select value={worldSlug} onChange={(event) => setWorldSlug(event.target.value)} className={fieldClass}>
            {worldOptions.map((slug) => <option key={slug}>{slug}</option>)}
          </select>
        </Field>
        <Field label="Difficulty">
          <select value={difficulty} onChange={(event) => setDifficulty(event.target.value as AdminStory['difficulty'])} className={fieldClass}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </Field>
        <Field label="Price"><input type="number" min={0} value={price} onChange={(event) => setPrice(Number(event.target.value))} className={fieldClass} /></Field>
        <Field label="Sort order"><input type="number" min={0} value={sortOrder} onChange={(event) => setSortOrder(Number(event.target.value))} className={fieldClass} /></Field>
        <Field label="Prerequisite">
          <select value={prerequisite ?? ''} onChange={(event) => setPrerequisite(event.target.value ? Number(event.target.value) : null)} className={fieldClass}>
            <option value="">None</option>
            {stories.filter((candidate) => candidate.id !== story.id).map((candidate) => (
              <option key={candidate.id} value={candidate.id}>{candidate.title}</option>
            ))}
          </select>
        </Field>
      </div>
      <Field label="Summary"><textarea value={summary} onChange={(event) => setSummary(event.target.value)} className={textAreaClass} /></Field>
      <MutationMessage mutation={update} />
      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={update.isPending || !title.trim()} onClick={() => update.mutate(story.is_published)}>Save details</Button>
        <Button size="sm" variant="outline" disabled={update.isPending} onClick={() => update.mutate(!story.is_published)}>
          {story.is_published ? 'Move to draft' : 'Publish story'}
        </Button>
      </div>
    </div>
  )
}
