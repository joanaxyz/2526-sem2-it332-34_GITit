import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { ContentDefinitionInput } from '@/features/authoring/api/authoringApi'
import type { ContentDefinition } from '@/features/authoring/types'
import {
  formToDefinition,
  initialForm,
  type AuthoringForm,
  type AuthoredLevel,
} from '@/features/authoring/utils/authoringModel'
import type { JsonObject } from '@/shared/api/generated/apiTypes'
import { useAuthStore } from '@/shared/auth/useAuth'

import { ContentEditorPage } from './ContentEditorPage'

const mocks = vi.hoisted(() => ({
  chapters: vi.fn(),
  createChapter: vi.fn(),
  get: vi.fn(),
  create: vi.fn(),
  update: vi.fn(),
  validate: vi.fn(),
  publish: vi.fn(),
  commandForms: vi.fn(),
  adminChapters: vi.fn(),
  unsavedGuard: vi.fn(),
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
  useRealGuard: false,
}))

vi.mock('@/features/authoring/api/authoringApi', () => ({
  authoringApi: {
    chapters: mocks.chapters,
    createChapter: mocks.createChapter,
    get: mocks.get,
    create: mocks.create,
    update: mocks.update,
    validate: mocks.validate,
    publish: mocks.publish,
    commandForms: mocks.commandForms,
  },
}))

vi.mock('@/features/admin/api/adminApi', () => ({
  adminApi: { chapters: mocks.adminChapters },
}))

vi.mock('@/features/authoring/hooks/useUnsavedChangesGuard', async (importOriginal) => {
  const actual = await importOriginal<
    typeof import('@/features/authoring/hooks/useUnsavedChangesGuard')
  >()
  return {
    useUnsavedChangesGuard: (
      options: Parameters<typeof actual.useUnsavedChangesGuard>[0],
    ) => {
      mocks.unsavedGuard(options)
      actual.useUnsavedChangesGuard({
        ...options,
        when: mocks.useRealGuard && options.when,
      })
    },
  }
})

vi.mock('sonner', () => ({
  toast: { success: mocks.toastSuccess, error: mocks.toastError },
}))

vi.mock('@/features/authoring/components/BattleStageEditor', () => ({
  BattleStageEditor: () => <div data-testid="battle-stage-editor" />,
}))

vi.mock('@/features/authoring/components/ChapterLessonPagesEditor', () => ({
  ChapterLessonPagesEditor: () => <div data-testid="lesson-pages-editor" />,
}))

vi.mock('@/features/authoring/components/LevelsEditor', () => ({
  LevelsEditor: ({
    levels,
    onChange,
    commandFormOptions,
  }: {
    levels: AuthoredLevel[]
    onChange: (levels: AuthoredLevel[]) => void
    commandFormOptions: unknown[]
  }) => (
    <div data-testid="levels-editor" data-command-forms={commandFormOptions.length}>
      <button
        type="button"
        onClick={() => onChange(levels.map((level, index) => index === 0
          ? {
              ...level,
              problems: level.problems.map((problem, problemIndex) => problemIndex === 0
                ? { ...problem, initialStateText: '{bad' }
                : problem),
            }
          : level))}
      >
        Make structured JSON invalid
      </button>
    </div>
  ),
}))

const ordinaryChapter = { id: 3, title: 'Authored chapter' }
const officialChapter = { id: 9, title: 'Published chapter' }

function makeContent(overrides: Partial<ContentDefinition> = {}): ContentDefinition {
  return {
    id: 41,
    kind: 'adventure',
    owner_id: 2,
    chapter_id: 3,
    official_chapter_id: null,
    source_definition_id: null,
    visibility: 'private',
    status: 'draft',
    slug: 'loaded-adventure',
    title: 'Loaded adventure',
    summary: 'Loaded summary',
    tags: [],
    command_family: 'git status',
    difficulty: '',
    definition: formToDefinition({ ...initialForm('adventure'), title: 'Loaded adventure' }),
    validation_errors: [],
    published_at: null,
    created_at: '2026-08-06T00:00:00Z',
    updated_at: '2026-08-06T00:00:00Z',
    ...overrides,
  }
}

function contentFromInput(id: number, input: ContentDefinitionInput): ContentDefinition {
  return makeContent({
    id,
    kind: input.kind,
    slug: input.slug,
    title: input.title,
    summary: input.summary,
    command_family: input.command_family,
    difficulty: input.difficulty,
    tags: input.tags,
    visibility: input.visibility,
    chapter_id: input.chapter ?? null,
    official_chapter_id: input.official_chapter ?? null,
    definition: input.definition,
  })
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, resolve, reject }
}

function requireInput(input: ContentDefinitionInput | null): ContentDefinitionInput {
  if (!input) throw new Error('Expected the request payload to be captured.')
  return input
}

function setUser(isStaff: boolean) {
  useAuthStore.setState({
    accessToken: 'test-token',
    user: {
      id: isStaff ? 1 : 2,
      username: isStaff ? 'staff' : 'author',
      email: isStaff ? 'staff@example.com' : 'author@example.com',
      is_staff: isStaff,
    },
  })
}

function renderEditor(path: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  const router = createMemoryRouter(
    [
      { path: '/level-editor/new/:kind', element: <ContentEditorPage /> },
      { path: '/level-editor/:definitionId', element: <ContentEditorPage /> },
      { path: '/elsewhere', element: <div>Elsewhere</div> },
    ],
    { initialEntries: [path] },
  )
  const result = render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
  return { ...result, queryClient, router }
}

describe('ContentEditorPage workflow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.useRealGuard = false
    setUser(false)
    mocks.chapters.mockResolvedValue({ results: [ordinaryChapter] })
    mocks.adminChapters.mockResolvedValue({ results: [officialChapter] })
    mocks.commandForms.mockResolvedValue({ results: [] })
    mocks.createChapter.mockResolvedValue({ ...ordinaryChapter, slug: 'authored-chapter' })
    mocks.validate.mockResolvedValue({ valid: true, errors: [] })
  })

  afterEach(() => {
    cleanup()
    vi.restoreAllMocks()
    useAuthStore.setState({ accessToken: null, user: null })
  })

  it('saves the exact ordinary preset payload, replaces the route, and becomes clean', async () => {
    const expectedForm: AuthoringForm = { ...initialForm('adventure'), chapterId: ordinaryChapter.id }
    const expectedInput: ContentDefinitionInput = {
      kind: 'adventure',
      slug: 'new-adventure',
      title: 'New adventure',
      summary: '',
      command_family: 'git status',
      difficulty: '',
      tags: [],
      visibility: 'private',
      chapter: ordinaryChapter.id,
      official_chapter: null,
      definition: formToDefinition(expectedForm) as JsonObject,
    }
    const saved = contentFromInput(51, expectedInput)
    mocks.create.mockResolvedValue(saved)
    mocks.get.mockResolvedValue(saved)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    const destination = await screen.findByRole('combobox', { name: 'Chapter' })
    await waitFor(() => expect(destination).toHaveValue('3'))
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expectedInput))
    await waitFor(() => expect(router.state.location.pathname).toBe('/level-editor/51'))
    expect(router.state.location.search).toBe('')
    expect(router.state.historyAction).toBe('REPLACE')
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Saved'))
  })

  it('disables chapter creation while a save is pending', async () => {
    const request = deferred<ContentDefinition>()
    mocks.create.mockReturnValue(request.promise)
    renderEditor('/level-editor/new/adventure?chapter=3')

    const createChapterButton = await screen.findByRole('button', { name: /new chapter/i })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.create).toHaveBeenCalledTimes(1))
    expect(createChapterButton).toBeDisabled()
    fireEvent.click(createChapterButton)
    expect(mocks.createChapter).not.toHaveBeenCalled()

    await act(async () => request.resolve(makeContent({ id: 51 })))
  })

  it('uses the staff official destination and keeps payload fields mutually exclusive', async () => {
    setUser(true)
    let saved: ContentDefinition
    mocks.create.mockImplementation(async (input: ContentDefinitionInput) => {
      saved = contentFromInput(52, input)
      mocks.get.mockResolvedValue(saved)
      return saved
    })
    const { router } = renderEditor('/level-editor/new/adventure?official=1&chapter=9')

    const destination = await screen.findByRole('combobox', { name: 'Official chapter' })
    await waitFor(() => expect(destination).toHaveValue('9'))
    expect(mocks.adminChapters).toHaveBeenCalledTimes(1)
    expect(mocks.chapters).not.toHaveBeenCalled()
    expect(screen.queryByRole('button', { name: /new chapter/i })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /manage curriculum/i })).toBeInTheDocument()

    fireEvent.change(destination, { target: { value: '' } })
    expect(screen.getByRole('button', { name: /^save$/i })).toBeDisabled()
    fireEvent.change(destination, { target: { value: '9' } })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({
      chapter: null,
      official_chapter: 9,
    })))
    await waitFor(() => expect(router.state.location.pathname).toBe('/level-editor/52'))
    expect(router.state.location.search).toBe('?official=1')
  })

  it('derives official mode for a loaded staff edit without a query flag', async () => {
    setUser(true)
    const loaded = makeContent({ id: 61, chapter_id: null, official_chapter_id: 9 })
    mocks.get.mockResolvedValue(loaded)
    mocks.update.mockResolvedValue(loaded)
    renderEditor('/level-editor/61')

    const destination = await screen.findByRole('combobox', { name: 'Official chapter' })
    await waitFor(() => expect(destination).toHaveValue('9'))
    expect(mocks.adminChapters).toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.update).toHaveBeenCalledWith(61, expect.objectContaining({
      chapter: null,
      official_chapter: 9,
    })))
  })

  it('ignores requested official mode for a non-staff author', async () => {
    let saved: ContentDefinition
    mocks.create.mockImplementation(async (input: ContentDefinitionInput) => {
      saved = contentFromInput(62, input)
      mocks.get.mockResolvedValue(saved)
      return saved
    })
    renderEditor('/level-editor/new/adventure?official=1&chapter=9')

    expect(await screen.findByRole('combobox', { name: 'Chapter' })).toHaveValue('')
    expect(mocks.chapters).toHaveBeenCalled()
    expect(mocks.adminChapters).not.toHaveBeenCalled()
    expect(screen.queryByRole('link', { name: /manage curriculum/i })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({
      chapter: null,
      official_chapter: null,
    })))
  })

  it('tracks loaded edits through dirty, PATCH, clean, and dirty-again states', async () => {
    const loaded = makeContent({ id: 71 })
    mocks.get.mockResolvedValue(loaded)
    mocks.update.mockImplementation(async (_id: number, input: ContentDefinitionInput) => contentFromInput(71, input))
    renderEditor('/level-editor/71')

    const title = await screen.findByRole('textbox', { name: 'Title' })
    expect(screen.getByRole('status')).toHaveTextContent('Saved')
    fireEvent.change(title, { target: { value: 'Edited once' } })
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
    expect(mocks.unsavedGuard).toHaveBeenLastCalledWith({
      when: true,
      allowedNextLocation: null,
    })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    await waitFor(() => expect(mocks.update).toHaveBeenCalledWith(71, expect.objectContaining({ title: 'Edited once' })))
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Saved'))
    expect(mocks.unsavedGuard).toHaveBeenLastCalledWith({
      when: false,
      allowedNextLocation: null,
    })
    fireEvent.change(screen.getByRole('textbox', { name: 'Title' }), { target: { value: 'Edited twice' } })
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
  })

  it('retains a rejected draft and requires a clean revision before publish', async () => {
    const loaded = makeContent({ id: 72, title: 'Server title' })
    mocks.get.mockResolvedValue(loaded)
    mocks.update.mockRejectedValue(new Error('Published definitions cannot be edited.'))
    renderEditor('/level-editor/72')

    const title = await screen.findByRole('textbox', { name: 'Title' })
    fireEvent.change(title, { target: { value: 'Local draft title' } })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Published definitions cannot be edited.')
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('Local draft title')
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
    expect(screen.getByRole('button', { name: /^validate$/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /^publish$/i })).toBeDisabled()
    expect(mocks.publish).not.toHaveBeenCalled()
  })

  it('publishes a clean persisted revision and adopts the server baseline', async () => {
    const loaded = makeContent({ id: 73, title: 'Server title' })
    mocks.get.mockResolvedValue(loaded)
    mocks.publish.mockResolvedValue(makeContent({
      id: 73,
      title: 'Published server title',
      status: 'published',
    }))
    renderEditor('/level-editor/73')

    expect(await screen.findByRole('textbox', { name: 'Title' })).toHaveValue('Server title')
    fireEvent.click(screen.getByRole('button', { name: /^publish$/i }))

    await waitFor(() => expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('Published server title'))
    expect(screen.getByRole('status')).toHaveTextContent('Saved')
  })

  it('rekeys a new save without prompting and preserves a newer edit as dirty', async () => {
    const request = deferred<ContentDefinition>()
    let submittedInput: ContentDefinitionInput | null = null
    mocks.create.mockImplementation((input: ContentDefinitionInput) => {
      submittedInput = input
      return request.promise
    })
    mocks.useRealGuard = true
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    const title = await screen.findByRole('textbox', { name: 'Title' })
    fireEvent.change(title, { target: { value: 'Submitted title' } })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))
    await waitFor(() => expect(mocks.create).toHaveBeenCalledTimes(1))
    fireEvent.change(screen.getByRole('textbox', { name: 'Title' }), {
      target: { value: 'Newer local title' },
    })

    const saved = contentFromInput(91, requireInput(submittedInput))
    mocks.get.mockResolvedValue(saved)
    await act(async () => request.resolve(saved))

    await waitFor(() => expect(router.state.location.pathname).toBe('/level-editor/91'))
    expect(confirm).not.toHaveBeenCalled()
    expect(await screen.findByRole('textbox', { name: 'Title' })).toHaveValue('Newer local title')
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')

    await act(async () => router.navigate('/level-editor/91#other'))
    await waitFor(() => expect(confirm).toHaveBeenCalledTimes(1))
    expect(router.state.location.pathname).toBe('/level-editor/91')
    expect(router.state.location.hash).toBe('')
  })

  it('ignores a stale new-save response after confirmed mode and preset navigation', async () => {
    setUser(true)
    const request = deferred<ContentDefinition>()
    let submittedInput: ContentDefinitionInput | null = null
    mocks.create.mockImplementation((input: ContentDefinitionInput) => {
      submittedInput = input
      return request.promise
    })
    mocks.useRealGuard = true
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    fireEvent.change(await screen.findByRole('textbox', { name: 'Title' }), {
      target: { value: 'Old source title' },
    })
    fireEvent.click(screen.getByRole('button', { name: /^save$/i }))
    await waitFor(() => expect(mocks.create).toHaveBeenCalledTimes(1))
    await act(async () => router.navigate('/level-editor/new/adventure?official=1&chapter=9'))

    await waitFor(() => expect(confirm).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(router.state.location.search).toBe('?official=1&chapter=9'))
    expect(await screen.findByRole('combobox', { name: 'Official chapter' })).toHaveValue('9')
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')

    await act(async () => request.resolve(contentFromInput(
      92,
      requireInput(submittedInput),
    )))

    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Saved'))
    expect(router.state.location.pathname).toBe('/level-editor/new/adventure')
    expect(router.state.location.search).toBe('?official=1&chapter=9')
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
    expect(mocks.toastSuccess).not.toHaveBeenCalled()
  })

  it('preserves an edit made while a clean publish is pending', async () => {
    const loaded = makeContent({ id: 74, title: 'Persisted title' })
    const request = deferred<ContentDefinition>()
    mocks.get.mockResolvedValue(loaded)
    mocks.publish.mockReturnValue(request.promise)
    renderEditor('/level-editor/74')

    expect(await screen.findByRole('textbox', { name: 'Title' })).toHaveValue('Persisted title')
    fireEvent.click(screen.getByRole('button', { name: /^publish$/i }))
    await waitFor(() => expect(mocks.publish).toHaveBeenCalledWith(74))
    fireEvent.change(screen.getByRole('textbox', { name: 'Title' }), {
      target: { value: 'Newer local title' },
    })
    await act(async () => request.resolve(makeContent({
      id: 74,
      title: 'Published server title',
      status: 'published',
    })))

    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('Newer local title')
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
    expect(screen.getByRole('button', { name: /^publish$/i })).toBeDisabled()
  })

  it('merges a created chapter into the latest same-source form', async () => {
    const request = deferred<{ id: number; title: string; slug: string }>()
    const createdChapter = { id: 4, title: 'Created chapter', slug: 'created-chapter' }
    mocks.createChapter.mockReturnValue(request.promise)
    renderEditor('/level-editor/new/adventure?chapter=3')

    await screen.findByRole('combobox', { name: 'Chapter' })
    fireEvent.click(screen.getByRole('button', { name: /new chapter/i }))
    fireEvent.change(screen.getByRole('textbox', { name: 'Title' }), {
      target: { value: 'Edited while creating' },
    })
    mocks.chapters.mockResolvedValue({ results: [ordinaryChapter, createdChapter] })
    await act(async () => request.resolve(createdChapter))

    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('Edited while creating')
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Chapter' })).toHaveValue('4'))
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
  })

  it('creates a chapter from a clean materialized form after preset navigation', async () => {
    const secondChapter = { id: 5, title: 'Second chapter', slug: 'second-chapter' }
    const createdChapter = { id: 6, title: 'Created chapter', slug: 'created-chapter' }
    const request = deferred<typeof createdChapter>()
    mocks.chapters.mockResolvedValue({ results: [ordinaryChapter, secondChapter] })
    mocks.createChapter.mockReturnValue(request.promise)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    const destination = await screen.findByRole('combobox', { name: 'Chapter' })
    await waitFor(() => expect(destination).toHaveValue('3'))
    await act(async () => router.navigate('/level-editor/new/adventure?chapter=5'))
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Chapter' })).toHaveValue('5'))
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
    expect(screen.getByRole('status')).toHaveTextContent('Saved')

    fireEvent.click(screen.getByRole('button', { name: /new chapter/i }))
    mocks.chapters.mockResolvedValue({
      results: [ordinaryChapter, secondChapter, createdChapter],
    })
    await act(async () => request.resolve(createdChapter))

    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Chapter' })).toHaveValue('6'))
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
    expect(screen.getByRole('status')).toHaveTextContent('Unsaved changes')
  })

  it('does not resurrect a discarded draft after confirmed source navigation', async () => {
    const secondChapter = { id: 5, title: 'Second chapter', slug: 'second-chapter' }
    mocks.chapters.mockResolvedValue({ results: [ordinaryChapter, secondChapter] })
    mocks.useRealGuard = true
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    fireEvent.change(await screen.findByRole('textbox', { name: 'Title' }), {
      target: { value: 'Discard this draft' },
    })
    await act(async () => router.navigate('/level-editor/new/adventure?chapter=5'))
    await waitFor(() => expect(confirm).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Chapter' })).toHaveValue('5'))
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')

    await act(async () => router.navigate('/level-editor/new/adventure?chapter=3'))
    await waitFor(() => expect(screen.getByRole('combobox', { name: 'Chapter' })).toHaveValue('3'))
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
    expect(screen.getByRole('status')).toHaveTextContent('Saved')
  })

  it('discards the old draft before a slow edit source finishes loading', async () => {
    const detailRequest = deferred<ContentDefinition>()
    mocks.get.mockReturnValue(detailRequest.promise)
    mocks.useRealGuard = true
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(true)
    const { router } = renderEditor('/level-editor/new/adventure?chapter=3')

    fireEvent.change(await screen.findByRole('textbox', { name: 'Title' }), {
      target: { value: 'Discard before loading' },
    })
    await act(async () => router.navigate('/level-editor/82'))
    await waitFor(() => expect(confirm).toHaveBeenCalledTimes(1))
    expect(await screen.findByText('Loading content')).toBeInTheDocument()
    await waitFor(() => expect(mocks.unsavedGuard).toHaveBeenLastCalledWith({
      when: false,
      allowedNextLocation: null,
    }))

    await act(async () => router.navigate(-1))
    await waitFor(() => expect(router.state.location.pathname).toBe('/level-editor/new/adventure'))
    expect(await screen.findByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
    expect(screen.getByRole('status')).toHaveTextContent('Saved')
    expect(confirm).toHaveBeenCalledTimes(1)

    await act(async () => detailRequest.resolve(makeContent({ id: 82 })))
    expect(router.state.location.pathname).toBe('/level-editor/new/adventure')
    expect(screen.getByRole('textbox', { name: 'Title' })).toHaveValue('New adventure')
  })

  it('never requests command forms for new or unresolved loaded lessons', async () => {
    const first = renderEditor('/level-editor/new/lesson')
    expect(await screen.findByTestId('lesson-pages-editor')).toBeInTheDocument()
    expect(mocks.commandForms).not.toHaveBeenCalled()
    first.unmount()
    first.queryClient.clear()

    let resolveLesson: (value: ContentDefinition) => void = () => undefined
    mocks.get.mockReturnValue(new Promise<ContentDefinition>((resolve) => { resolveLesson = resolve }))
    renderEditor('/level-editor/81')
    expect(await screen.findByText('Loading content')).toBeInTheDocument()
    expect(mocks.commandForms).not.toHaveBeenCalled()
    await act(async () => resolveLesson(makeContent({
      id: 81,
      kind: 'lesson',
      slug: 'loaded-lesson',
      title: 'Loaded lesson',
      command_family: '',
      chapter_id: 3,
      definition: formToDefinition(initialForm('lesson')),
    })))

    expect(await screen.findByTestId('lesson-pages-editor')).toBeInTheDocument()
    expect(mocks.commandForms).not.toHaveBeenCalled()
    expect(screen.queryByTestId('levels-editor')).not.toBeInTheDocument()
  })

  it('exposes raw disclosure state and the current structured-input error', async () => {
    renderEditor('/level-editor/new/adventure')
    expect(await screen.findByTestId('levels-editor')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Make structured JSON invalid' }))
    const disclosure = screen.getByRole('button', { name: /show the generated json/i })
    expect(disclosure).toHaveAttribute('aria-expanded', 'false')
    expect(disclosure).toHaveAttribute('aria-controls', 'content-editor-generated-json')
    fireEvent.click(disclosure)

    expect(screen.getByRole('button', { name: /hide the generated json/i })).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText('Problem "wave-one" initial state is not valid JSON.')).toHaveAttribute(
      'id',
      'content-editor-generated-json',
    )
  })
})
