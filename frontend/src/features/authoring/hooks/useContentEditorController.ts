import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { toast } from 'sonner'

import { adminApi } from '@/features/admin/api/adminApi'
import { authoringApi, type ContentDefinitionInput } from '@/features/authoring/api/authoringApi'
import {
  mergeCreatedChapter,
  newDraftSourceKey,
  reconcileSavedDraft,
  sameForm,
  type DraftState,
} from '@/features/authoring/hooks/contentEditorDraftState'
import { useUnsavedChangesGuard } from '@/features/authoring/hooks/useUnsavedChangesGuard'
import type { ContentKind } from '@/features/authoring/types'
import {
  definitionErrorMessage,
  formFromContent,
  formToDefinition,
  initialForm,
  type AuthoringForm,
} from '@/features/authoring/utils/authoringModel'
import type { JsonObject } from '@/shared/api/generated/apiTypes'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'

type SaveSubmission = DraftState & {
  definitionId: number | null
  isNew: boolean
  isOfficialMode: boolean
}
type ExistingSubmission = DraftState & { definitionId: number }
type ChapterSubmission = DraftState & { title: string }
type FormErrorState = { sourceKey: string; message: string }

export function useContentEditorController() {
  const { definitionId, kind } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const user = useAuthStore((state) => state.user)
  const parsedId = definitionId ? Number(definitionId) : null
  const newKind = (kind || 'adventure') as ContentKind
  const isNew = parsedId === null
  const requestedOfficialMode = searchParams.get('official') === '1'
  const presetChapterId = searchParams.get('chapter') ? Number(searchParams.get('chapter')) : null
  const initialSourceKey = newDraftSourceKey(newKind, requestedOfficialMode, presetChapterId)
  const sourceKey = isNew ? initialSourceKey : `content:${parsedId}`
  const initialNewForm = useMemo(
    () => ({
      ...initialForm(newKind),
      chapterId: requestedOfficialMode ? null : presetChapterId,
      officialChapterId: requestedOfficialMode ? presetChapterId : null,
    }),
    [newKind, presetChapterId, requestedOfficialMode],
  )
  const [draft, setDraft] = useState<DraftState>(() => ({
    sourceKey: initialSourceKey,
    form: initialNewForm,
  }))
  const [savedSnapshot, setSavedSnapshot] = useState<DraftState | null>(null)
  const [formErrorState, setFormErrorState] = useState<FormErrorState | null>(null)
  const [internalNavigationTarget, setInternalNavigationTarget] = useState<string | null>(null)
  const currentSourceKeyRef = useRef(sourceKey)
  const materializedSourceKeyRef = useRef(draft.sourceKey)
  const pendingLoadedSourceKeyRef = useRef<string | null>(null)
  currentSourceKeyRef.current = sourceKey

  const detail = useQuery({
    queryKey: parsedId !== null
      ? queryKeys.authoringContentDetail(parsedId)
      : ['authoring-content-new', newKind],
    queryFn: () => authoringApi.get(parsedId as number),
    enabled: parsedId !== null,
  })
  const isOfficialMode = Boolean(
    user?.is_staff && (requestedOfficialMode || detail.data?.official_chapter_id != null),
  )
  const chaptersQuery = useQuery({
    queryKey: queryKeys.authoringChapters,
    queryFn: authoringApi.chapters,
    enabled: !isOfficialMode,
  })
  const officialChaptersQuery = useQuery({
    queryKey: queryKeys.adminChapters(),
    queryFn: () => adminApi.chapters(),
    enabled: isOfficialMode,
  })
  const effectiveKind = isNew ? newKind : detail.data?.kind
  const commandFormsQuery = useQuery({
    queryKey: ['authoring-command-forms'],
    queryFn: authoringApi.commandForms,
    staleTime: 5 * 60 * 1000,
    enabled: effectiveKind != null && effectiveKind !== 'lesson',
  })
  const chapters = useMemo(
    () => (isOfficialMode
      ? (officialChaptersQuery.data?.results ?? [])
      : (chaptersQuery.data?.results ?? [])
    ).map((chapter) => ({ id: chapter.id, title: chapter.title })),
    [chaptersQuery.data, isOfficialMode, officialChaptersQuery.data],
  )

  const loadedForm = useMemo(() => (detail.data ? formFromContent(detail.data) : null), [detail.data])
  const form = draft.sourceKey === sourceKey ? draft.form : loadedForm ?? initialNewForm
  const baselineForm = savedSnapshot?.sourceKey === sourceKey
    ? savedSnapshot.form
    : loadedForm ?? initialNewForm
  const isDirty = !sameForm(form, baselineForm)
  const formError = formErrorState?.sourceKey === sourceKey ? formErrorState.message : null

  useEffect(() => {
    const sourceChanged = materializedSourceKeyRef.current !== sourceKey
    const pendingLoadedSource = pendingLoadedSourceKeyRef.current === sourceKey
    if (!sourceChanged && !pendingLoadedSource) return
    if (sourceChanged) {
      materializedSourceKeyRef.current = sourceKey
      setSavedSnapshot((current) => current?.sourceKey === sourceKey ? current : null)
      setFormErrorState((current) => current?.sourceKey === sourceKey ? current : null)
    }
    if (!isNew && !loadedForm) {
      if (sourceChanged) {
        setDraft((current) => {
          if (current.sourceKey === sourceKey) {
            pendingLoadedSourceKeyRef.current = null
            return current
          }
          pendingLoadedSourceKeyRef.current = sourceKey
          return { sourceKey, form: initialNewForm }
        })
      }
      return
    }
    pendingLoadedSourceKeyRef.current = null
    const baseForm = loadedForm ?? initialNewForm
    setDraft((current) => sourceChanged && current.sourceKey === sourceKey
      ? current
      : { sourceKey, form: baseForm })
  }, [initialNewForm, isNew, loadedForm, sourceKey])

  function setForm(next: AuthoringForm) {
    setDraft({ sourceKey, form: next })
  }

  function buildInput(submittedForm: AuthoringForm, officialMode: boolean): ContentDefinitionInput {
    if (officialMode && !submittedForm.officialChapterId) {
      throw new Error('Choose a published official chapter before saving.')
    }
    return {
      kind: submittedForm.kind,
      slug: submittedForm.slug,
      title: submittedForm.title,
      summary: submittedForm.summary,
      command_family: submittedForm.commandFamily,
      difficulty: submittedForm.difficulty,
      tags: submittedForm.tags,
      visibility: submittedForm.visibility,
      chapter: officialMode ? null : submittedForm.chapterId,
      official_chapter: officialMode ? submittedForm.officialChapterId : null,
      definition: formToDefinition(submittedForm) as JsonObject,
    }
  }

  const createChapterMutation = useMutation({
    mutationFn: (submission: ChapterSubmission) => authoringApi.createChapter({ title: submission.title }),
    onSuccess: (chapter, submission) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringChapters })
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      setDraft((current) => mergeCreatedChapter(current, submission, chapter.id))
    },
    onError: (error, submission) => {
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      setFormErrorState({
        sourceKey: submission.sourceKey,
        message: definitionErrorMessage(error)
          ?? (error instanceof Error ? error.message : 'Could not create chapter.'),
      })
    },
  })
  const saveMutation = useMutation({
    mutationFn: async (submission: SaveSubmission) => {
      const input = buildInput(submission.form, submission.isOfficialMode)
      return submission.isNew
        ? authoringApi.create(input)
        : authoringApi.update(submission.definitionId as number, input)
    },
    onSuccess: (saved, submission) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringChapters })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(saved.id) })
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      const savedState = { sourceKey: `content:${saved.id}`, form: formFromContent(saved) }
      setSavedSnapshot(savedState)
      setDraft((current) => reconcileSavedDraft(current, submission, savedState))
      toast.success('Draft saved.')
      if (submission.isNew) {
        setInternalNavigationTarget(
          `/level-editor/${saved.id}${submission.isOfficialMode ? '?official=1' : ''}`,
        )
      }
    },
    onError: (error, submission) => {
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      const message = definitionErrorMessage(error)
        ?? (error instanceof Error ? error.message : 'Could not save.')
      setFormErrorState({ sourceKey: submission.sourceKey, message })
      toast.error(message)
    },
  })
  const validateMutation = useMutation({
    mutationFn: (submission: ExistingSubmission) => authoringApi.validate(submission.definitionId),
    onSuccess: (result, submission) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(submission.definitionId) })
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      if (result.valid) toast.success('Validation passed.')
      else toast.error(`${result.errors.length} validation issue${result.errors.length === 1 ? '' : 's'} found.`)
    },
    onError: (error, submission) => {
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      const message = error instanceof Error ? error.message : 'Could not validate.'
      setFormErrorState({ sourceKey: submission.sourceKey, message })
      toast.error(message)
    },
  })
  const publishMutation = useMutation({
    mutationFn: (submission: ExistingSubmission) => authoringApi.publish(submission.definitionId),
    onSuccess: (published, submission) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContent() })
      queryClient.invalidateQueries({ queryKey: queryKeys.authoringContentDetail(submission.definitionId) })
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      const publishedState = { sourceKey: `content:${published.id}`, form: formFromContent(published) }
      setSavedSnapshot(publishedState)
      setDraft((current) => reconcileSavedDraft(current, submission, publishedState))
      toast.success('Published.')
    },
    onError: (error, submission) => {
      if (currentSourceKeyRef.current !== submission.sourceKey) return
      const message = error instanceof Error ? error.message : 'Could not publish.'
      setFormErrorState({ sourceKey: submission.sourceKey, message })
      toast.error(message)
    },
  })

  const canUseActions = !isNew && parsedId !== null
  const officialDestinationMissing = isOfficialMode && !form.officialChapterId
  const busy = createChapterMutation.isPending
    || saveMutation.isPending || validateMutation.isPending || publishMutation.isPending
  useUnsavedChangesGuard({
    when: isDirty || busy,
    allowedNextLocation: internalNavigationTarget,
  })
  useEffect(() => {
    if (!internalNavigationTarget) return
    navigate(internalNavigationTarget, { replace: true })
    setInternalNavigationTarget(null)
  }, [internalNavigationTarget, navigate])

  return {
    form, setForm, sourceKey, isNew, isOfficialMode, chapters,
    commandFormOptions: commandFormsQuery.data?.results ?? [],
    isLoading: detail.isLoading,
    loadError: detail.isError ? detail.error.message : null,
    busy, isDirty, canUseActions, officialDestinationMissing,
    formError,
    validationErrors: detail.data?.validation_errors ?? [],
    save: () => {
      setFormErrorState(null)
      saveMutation.mutate({ sourceKey, form, definitionId: parsedId, isNew, isOfficialMode })
    },
    validate: () => {
      if (!isDirty && parsedId !== null) validateMutation.mutate({ sourceKey, form, definitionId: parsedId })
    },
    publish: () => {
      if (!isDirty && parsedId !== null) publishMutation.mutate({ sourceKey, form, definitionId: parsedId })
    },
    createChapter: () => {
      if (busy) return
      createChapterMutation.mutate({
        sourceKey,
        form,
        title: `Chapter ${chapters.length + 1}`,
      })
    },
  }
}
