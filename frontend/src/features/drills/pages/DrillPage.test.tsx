import { StrictMode } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { drillsApi } from '@/features/drills/api/drillsApi'
import { useDrillSession } from '@/features/drills/hooks/useDrillSession'
import type { DrillPlan, DrillResume } from '@/features/drills/types'
import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'
import { DrillPage } from './DrillPage'

vi.mock('@/features/drills/api/drillsApi', () => ({
  drillsApi: { getPlan: vi.fn(), saveRun: vi.fn(), reportSession: vi.fn(), discardRun: vi.fn() },
}))
vi.mock('@/features/drills/components/DrillSession', () => ({
  DrillSession: SessionProbe,
}))

function SessionProbe({ plan }: { plan: DrillPlan }) {
  const session = useDrillSession(plan)
  const rung = session.ask?.kind === 'card' ? session.ask.rung : null
  return (
    <div>
      <p>Answered {session.answered}</p>
      <p>{session.finished ? 'Finished' : rung}</p>
      <button onClick={() => session.setAnswer({
        kind: 'choice',
        value: rung === 'complete' ? 'add' : 'git add',
      })}>Choose</button>
      <button onClick={session.check}>Check</button>
      <button onClick={session.advance}>Continue</button>
      <button onClick={session.restart}>Restart</button>
    </div>
  )
}

function initialPlan(): DrillPlan {
  return {
    available: true,
    level: {
      id: 51, slug: 'stage-files', title: 'Stage files', description: '',
      chapter_id: 3, chapter_number: 1, chapter_title: 'Basics',
      story_slug: 'main', story_title: 'Main',
    },
    cards: [{
      key: 'add', command: 'git add', intent: 'Stage files', base_command: 'git add',
      summary: '', tokens: ['git', 'add'], bank: ['git', 'add', 'status'],
      command_choices: [{ value: 'git status', gloss: 'Inspect' }, { value: 'git init', gloss: 'Create' }],
      intent_choices: [],
      blank: { index: 1, answer: 'add', options: [{ value: 'status', gloss: 'Inspect' }] },
    }],
    sequence: null,
    resume: null,
    progress: {
      best_accuracy: 0, cleared: false, clears: 0, first_cleared_at: null,
      last_accuracy: 0, last_played_at: null, sessions: 0, shaky_form_keys: [],
    },
  }
}

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((done) => { resolve = done })
  return { promise, resolve }
}

let serverPlan: DrillPlan
let calls: string[]
const clients: QueryClient[] = []

function client() {
  const value = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  })
  clients.push(value)
  return value
}

function save(body: Parameters<typeof drillsApi.saveRun>[1]) {
  const resume: DrillResume = {
    id: 7, answered: body.answered, correct: body.correct, updated_at: '2026-10-01T00:00:00Z',
    queue_state: {
      cards: body.cards, queue: body.queue, sequencePending: body.sequence_pending ?? false,
      answered: body.answered, correct: body.correct,
    },
  }
  serverPlan = { ...serverPlan, resume }
  return { resume }
}

function mount(queryClient: QueryClient) {
  return render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/drills/51']}>
          <Routes><Route path="/drills/:levelId" element={<DrillPage />} /></Routes>
        </MemoryRouter>
      </QueryClientProvider>
    </StrictMode>,
  )
}

function answer() {
  fireEvent.click(screen.getByText('Choose'))
  fireEvent.click(screen.getByText('Check'))
  fireEvent.click(screen.getByText('Continue'))
}

describe('drill checkpoint lifecycle', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    serverPlan = initialPlan()
    calls = []
    useAuthStore.getState().setSession('learner-token', {
      id: 1, username: 'learner', email: 'learner@example.com', is_staff: false,
    })
    vi.mocked(drillsApi.getPlan).mockImplementation(async () => serverPlan)
    vi.mocked(drillsApi.saveRun).mockImplementation(async (_id, body) => {
      calls.push(`save:${body.answered}`)
      return save(body)
    })
    vi.mocked(drillsApi.reportSession).mockImplementation(async () => {
      calls.push('report')
      serverPlan = {
        ...serverPlan, resume: null,
        progress: { ...serverPlan.progress, cleared: true, clears: 1, sessions: 1 },
      }
      return { progress: serverPlan.progress }
    })
    vi.mocked(drillsApi.discardRun).mockImplementation(async () => {
      calls.push('discard')
      serverPlan = { ...serverPlan, resume: null }
      return { resume: null }
    })
  })

  afterEach(() => {
    cleanup()
    for (const value of clients.splice(0)) value.clear()
  })

  it('waits for a fresh resume instead of hydrating a cached plan on entry', async () => {
    const queryClient = client()
    queryClient.setQueryData(queryKeys.levelDrill(51), serverPlan)
    const pending = deferred<DrillPlan>()
    vi.mocked(drillsApi.getPlan).mockReturnValueOnce(pending.promise)
    mount(queryClient)
    expect(screen.queryByText('Answered 0')).not.toBeInTheDocument()
    await act(async () => pending.resolve(serverPlan))
    expect(await screen.findByText('Answered 0')).toBeInTheDocument()
  })

  it('resumes the saved question when returning while the previous save is pending', async () => {
    const pending = deferred<void>()
    vi.mocked(drillsApi.saveRun).mockImplementationOnce(async (_id, body) => {
      await pending.promise
      return save(body)
    })
    const queryClient = client()
    const first = mount(queryClient)
    await screen.findByText('Answered 0')
    answer()
    await waitFor(() => expect(drillsApi.saveRun).toHaveBeenCalledTimes(1))
    first.unmount()
    mount(queryClient)
    expect(screen.queryByText('Answered 0')).not.toBeInTheDocument()
    expect(drillsApi.getPlan).toHaveBeenCalledTimes(1)
    await act(async () => pending.resolve())
    expect(await screen.findByText('Answered 1')).toBeInTheDocument()
    expect(screen.getByText('complete')).toBeInTheDocument()
    expect(drillsApi.getPlan).toHaveBeenCalledTimes(2)
    // StrictMode must not issue a checkpoint twice through an updater replay.
    expect(drillsApi.saveRun).toHaveBeenCalledTimes(1)
  })

  it('orders pending saves, completion, restart, and a new checkpoint', async () => {
    const pending = deferred<void>()
    vi.mocked(drillsApi.saveRun).mockImplementationOnce(async (_id, body) => {
      calls.push(`save:${body.answered}`)
      await pending.promise
      return save(body)
    })
    const queryClient = client()
    const first = mount(queryClient)
    await screen.findByText('Answered 0')
    answer()
    await waitFor(() => expect(calls).toEqual(['save:1']))
    answer()
    answer()
    expect(screen.getByText('Finished')).toBeInTheDocument()
    fireEvent.click(screen.getByText('Restart'))
    answer()
    expect(drillsApi.reportSession).not.toHaveBeenCalled()
    expect(drillsApi.discardRun).not.toHaveBeenCalled()
    await act(async () => pending.resolve())
    await waitFor(() => expect(calls).toEqual(['save:1', 'save:2', 'report', 'discard', 'save:1']))
    await waitFor(() => expect(queryClient.isMutating()).toBe(0))
    expect(serverPlan.resume?.answered).toBe(1)
    expect(serverPlan.progress.sessions).toBe(1)
    first.unmount()
    mount(queryClient)
    expect(await screen.findByText('Answered 1')).toBeInTheDocument()
  })

  it('keeps reentry loading through intermediate cache updates and the final GET', async () => {
    const firstSave = deferred<void>()
    const secondSave = deferred<void>()
    const entryRead = deferred<DrillPlan>()
    vi.mocked(drillsApi.saveRun)
      .mockImplementationOnce(async (_id, body) => {
        await firstSave.promise
        return save(body)
      })
      .mockImplementationOnce(async (_id, body) => {
        await secondSave.promise
        return save(body)
      })
    const queryClient = client()
    const first = mount(queryClient)
    await screen.findByText('Answered 0')
    answer()
    await waitFor(() => expect(drillsApi.saveRun).toHaveBeenCalledTimes(1))
    answer()
    first.unmount()
    vi.mocked(drillsApi.getPlan).mockReturnValueOnce(entryRead.promise)
    mount(queryClient)
    await act(async () => firstSave.resolve())
    await waitFor(() => expect(drillsApi.saveRun).toHaveBeenCalledTimes(2))
    expect(queryClient.getQueryData<DrillPlan>(queryKeys.levelDrill(51))?.resume?.answered).toBe(1)
    expect(screen.queryByText('Answered 1')).not.toBeInTheDocument()
    await act(async () => secondSave.resolve())
    await waitFor(() => expect(drillsApi.getPlan).toHaveBeenCalledTimes(2))
    expect(screen.queryByText('Answered 2')).not.toBeInTheDocument()
    await act(async () => entryRead.resolve(serverPlan))
    expect(await screen.findByText('Answered 2')).toBeInTheDocument()
    expect(screen.getByText('forge')).toBeInTheDocument()
  })

  it('does not restore a finished checkpoint on the next visit', async () => {
    const queryClient = client()
    const first = mount(queryClient)
    await screen.findByText('Answered 0')
    answer()
    answer()
    answer()
    await waitFor(() => expect(drillsApi.reportSession).toHaveBeenCalledTimes(1))
    await waitFor(() => expect(queryClient.isMutating()).toBe(0))
    expect(queryClient.getQueryData<DrillPlan>(queryKeys.levelDrill(51))?.resume).toBeNull()
    first.unmount()
    mount(queryClient)
    expect(await screen.findByText('Answered 0')).toBeInTheDocument()
    expect(drillsApi.reportSession).toHaveBeenCalledTimes(1)
  })

  it('refuses to send a queued checkpoint after an account change', async () => {
    const pending = deferred<void>()
    vi.mocked(drillsApi.saveRun).mockImplementationOnce(async (_id, body) => {
      await pending.promise
      return save(body)
    })
    const queryClient = client()
    mount(queryClient)
    await screen.findByText('Answered 0')
    answer()
    await waitFor(() => expect(drillsApi.saveRun).toHaveBeenCalledTimes(1))
    answer()
    useAuthStore.getState().clearSession()
    await act(async () => pending.resolve())
    await waitFor(() => expect(queryClient.isMutating()).toBe(0))
    expect(drillsApi.saveRun).toHaveBeenCalledTimes(1)
  })
})
