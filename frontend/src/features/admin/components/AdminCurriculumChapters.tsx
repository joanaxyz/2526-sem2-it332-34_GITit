import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import {
  adminApi,
  type AdminChapter,
  type AdminStory,
} from '@/features/admin/api/adminApi'
import {
  CurriculumField as Field,
  CurriculumMutationMessage as MutationMessage,
  CurriculumStatusPill as StatusPill,
  fieldClass,
  textAreaClass,
} from '@/features/admin/components/AdminCurriculumUi'
import type { JsonObject } from '@/shared/api/generated/apiTypes'
import { queryKeys } from '@/shared/api/queryKeys'
import { Button } from '@/shared/components/Button'
import { LoadingState } from '@/shared/components/LoadingState'

export function AdminCurriculumChapters({ story }: { story: AdminStory }) {
  const queryClient = useQueryClient()
  const chaptersQuery = useQuery({
    queryKey: queryKeys.adminChapters(story.id),
    queryFn: () => adminApi.chapters(story.id),
  })
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.adminChapters(story.id) })
    queryClient.invalidateQueries({ queryKey: queryKeys.adminStories })
  }

  if (chaptersQuery.isPending) {
    return <LoadingState label="Loading chapters" variant="inline" />
  }
  if (chaptersQuery.isError) {
    return <p className="text-xs text-destructive">Could not load chapters.</p>
  }

  return (
    <div className="grid gap-3 border-t border-border/60 pt-4">
      <h3 className="text-sm font-bold text-foreground">Chapters</h3>
      <CreateChapter
        storyId={story.id}
        nextNumber={chaptersQuery.data.results.length + 1}
        onCreated={invalidate}
      />
      {chaptersQuery.data.results.length === 0 ? (
        <p className="text-xs text-muted-foreground">
          No chapters yet. Add one before publishing this story.
        </p>
      ) : (
        <div className="grid gap-2">
          {chaptersQuery.data.results.map((chapter) => (
            <ChapterRow key={chapter.id} chapter={chapter} onChanged={invalidate} />
          ))}
        </div>
      )}
    </div>
  )
}

function CreateChapter({
  storyId,
  nextNumber,
  onCreated,
}: {
  storyId: number
  nextNumber: number
  onCreated: () => void
}) {
  const [slug, setSlug] = useState('')
  const [title, setTitle] = useState('')
  const [number, setNumber] = useState(nextNumber)
  const create = useMutation({
    mutationFn: () => adminApi.createChapter({ story_id: storyId, slug, title, number }),
    onSuccess: () => {
      setSlug('')
      setTitle('')
      setNumber((value) => value + 1)
      onCreated()
    },
  })

  return (
    <form
      className="grid gap-2 rounded-md bg-background/40 p-3 md:grid-cols-[1fr_1fr_7rem_auto]"
      onSubmit={(event) => {
        event.preventDefault()
        if (slug.trim() && title.trim()) create.mutate()
      }}
    >
      <Field label="Chapter slug">
        <input
          required
          value={slug}
          onChange={(event) => setSlug(event.target.value)}
          className={fieldClass}
        />
      </Field>
      <Field label="Title">
        <input
          required
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className={fieldClass}
        />
      </Field>
      <Field label="Number">
        <input
          required
          type="number"
          min={1}
          value={number}
          onChange={(event) => setNumber(Number(event.target.value))}
          className={fieldClass}
        />
      </Field>
      <Button type="submit" size="sm" className="self-end" disabled={create.isPending}>
        Add draft
      </Button>
      <div className="md:col-span-4">
        <MutationMessage mutation={create} />
      </div>
    </form>
  )
}

function ChapterRow({
  chapter,
  onChanged,
}: {
  chapter: AdminChapter
  onChanged: () => void
}) {
  const [number, setNumber] = useState(chapter.number)
  const [title, setTitle] = useState(chapter.title)
  const [description, setDescription] = useState(chapter.description)
  const [sortOrder, setSortOrder] = useState(chapter.sort_order)
  const [isPublished, setPublished] = useState(chapter.is_published)
  const [isPlayable, setPlayable] = useState(chapter.is_playable)
  const [battleStage, setBattleStage] = useState(
    JSON.stringify(chapter.battle_stage, null, 2),
  )
  const update = useMutation({
    mutationFn: () =>
      adminApi.updateChapter(chapter.id, {
        number,
        title,
        description,
        sort_order: sortOrder,
        is_published: isPublished,
        is_playable: isPlayable,
        battle_stage: parseBattleStage(battleStage),
      }),
    onSuccess: onChanged,
  })

  return (
    <div className="grid gap-3 rounded-md border border-border/60 bg-background/30 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <strong className="text-sm text-foreground">
          #{chapter.number} {chapter.title}
        </strong>
        <StatusPill active={chapter.is_published} />
        <span className="text-[11px] uppercase text-muted-foreground">
          {chapter.management_source}
        </span>
      </div>
      <div className="grid gap-2 md:grid-cols-[7rem_1fr_7rem]">
        <Field label="Number">
          <input
            type="number"
            min={1}
            value={number}
            onChange={(event) => setNumber(Number(event.target.value))}
            className={fieldClass}
          />
        </Field>
        <Field label="Title">
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className={fieldClass}
          />
        </Field>
        <Field label="Sort">
          <input
            type="number"
            min={0}
            value={sortOrder}
            onChange={(event) => setSortOrder(Number(event.target.value))}
            className={fieldClass}
          />
        </Field>
      </div>
      <Field label="Description">
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          className={textAreaClass}
        />
      </Field>
      <Field label="Battle stage JSON">
        <textarea
          value={battleStage}
          onChange={(event) => setBattleStage(event.target.value)}
          className={textAreaClass}
          spellCheck={false}
        />
      </Field>
      <div className="flex flex-wrap gap-4 text-sm text-foreground">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={isPublished}
            onChange={(event) => {
              setPublished(event.target.checked)
              if (!event.target.checked) setPlayable(false)
            }}
          />
          Published
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={isPlayable}
            onChange={(event) => {
              setPlayable(event.target.checked)
              if (event.target.checked) setPublished(true)
            }}
          />
          Playable
        </label>
      </div>
      <MutationMessage mutation={update} />
      <Button
        size="sm"
        className="w-fit"
        disabled={update.isPending || !title.trim()}
        onClick={() => update.mutate()}
      >
        Save chapter
      </Button>
    </div>
  )
}

function parseBattleStage(value: string): JsonObject {
  const parsed: unknown = JSON.parse(value)
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('Battle stage must be a JSON object.')
  }
  return parsed as JsonObject
}
