import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { DrillSession } from './DrillSession'
import type { DrillPlan } from '@/features/drills/types'
import { useAuthStore } from '@/shared/auth/useAuth'
import { drillsApi } from '@/features/drills/api/drillsApi'

vi.mock('@/features/drills/api/drillsApi', () => ({ drillsApi: {
  saveRun: vi.fn(async () => ({ resume: null })),
  reportSession: vi.fn(async () => ({ progress: null })),
  discardRun: vi.fn(async () => ({ resume: null })),
} }))
vi.mock('@/shared/mascot/MascotSprite', () => ({
  MascotSprite: ({ pose }: { pose: string }) => <span data-testid="pose">{pose}</span>,
}))

const plan: DrillPlan = {
  available: true,
  level: { id: 51, slug: 'stage-files', title: 'Stage files', description: '', chapter_id: 3,
    chapter_number: 1, chapter_title: 'Basics', story_slug: 'main', story_title: 'Main' },
  cards: [{
    key: 'add', command: 'git add', intent: 'Stage files', base_command: 'git add', summary: '',
    tokens: ['git', 'add'], bank: ['git', 'add', 'status'],
    command_choices: [{ value: 'git status', gloss: 'Inspect' }, { value: 'git init', gloss: 'Create' }],
    intent_choices: [], blank: { index: 1, answer: 'add', options: [{ value: 'status', gloss: 'Inspect' }] },
  }], sequence: null, resume: null,
  progress: { best_accuracy: 0, cleared: false, clears: 0, first_cleared_at: null,
    last_accuracy: 0, last_played_at: null, sessions: 0, shaky_form_keys: [] },
}

let client: QueryClient
function LocationProbe() {
  return <output data-testid="drill-location">{useLocation().pathname}</output>
}
function mount(customPlan = plan) {
  client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter initialEntries={['/drill/51']}>
    <DrillSession plan={customPlan} /><LocationProbe />
  </MemoryRouter></QueryClientProvider>)
}
async function advanceTime(ms: number) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms) })
}
async function reachCheckpoint() {
  fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
  await advanceTime(650)
  fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: add$/ }))
  await advanceTime(650)
}

describe('continuous flight session', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
    vi.stubGlobal('matchMedia', () => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
    HTMLElement.prototype.scrollIntoView = vi.fn()
    useAuthStore.getState().setSession('learner-token', { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false })
  })
  afterEach(() => { cleanup(); client?.clear(); vi.useRealTimers(); vi.unstubAllGlobals(); Reflect.deleteProperty(HTMLElement.prototype, 'scrollIntoView') })

  it('automatically sends the next question in the same arena after a brief correct hit', async () => {
    mount()
    const actor = document.querySelector('.drill-flight-actor')
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    expect(screen.getByRole('button', { name: 'Correct' })).toBeDisabled()
    expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument()
    await advanceTime(649)
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    await advanceTime(1)
    expect(screen.getByRole('region', { name: 'Fill the missing piece.' })).toHaveFocus()
    expect(document.querySelector('.drill-flight-actor')).toBe(actor)
    expect(screen.getByLabelText('3 of 3 lives remaining')).toBeInTheDocument()
    expect(drillsApi.saveRun).toHaveBeenCalledTimes(1)
  })

  it('automatically advances wrong hits and opens a detailed review after the last life', async () => {
    mount()
    for (let lives = 2; lives >= 0; lives--) {
      fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git status$/ }))
      expect(screen.getByRole('button', { name: 'Wrong' })).toBeDisabled()
      expect(screen.getByLabelText(`${lives} of 3 lives remaining`)).toBeInTheDocument()
      expect(screen.queryByText('Your answer')).not.toBeInTheDocument()
      if (lives > 0) {
        expect(screen.getByTestId('pose')).toHaveTextContent('float')
        await advanceTime(1000)
      }
    }
    expect(screen.getByTestId('pose')).toHaveTextContent('die')
    await advanceTime(1599)
    expect(screen.queryByRole('button', { name: 'Drill again' })).not.toBeInTheDocument()
    await advanceTime(1)
    const review = screen.getByRole('region', { name: 'Your flight review' })
    expect(within(review).getAllByText('git status')).toHaveLength(3)
    expect(within(review).getAllByText('git add')).toHaveLength(3)
    expect(within(review).getAllByText('Inspect')).toHaveLength(3)
    expect(drillsApi.reportSession).toHaveBeenCalledExactlyOnceWith(51, expect.objectContaining({ answers_total: 3, answers_correct: 0, completed: false }))
    fireEvent.click(screen.getByRole('button', { name: 'Drill again' }))
    expect(screen.getByLabelText('3 of 3 lives remaining')).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Your flight review' })).not.toBeInTheDocument()
  })

  it('ignores Enter during a hit so held keys cannot skip the response or double-score it', async () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    fireEvent.keyDown(window, { key: 'Enter', repeat: true })
    fireEvent.keyDown(window, { key: 'Enter' })
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    await advanceTime(650)
    expect(screen.getByRole('heading', { name: 'Fill the missing piece.' })).toBeInTheDocument()
    expect(drillsApi.saveRun).toHaveBeenCalledTimes(1)
  })

  it('automatically opens the summary after a successful walking checkpoint', async () => {
    mount()
    await reachCheckpoint()
    fireEvent.click(screen.getByRole('button', { name: 'git' }))
    fireEvent.click(screen.getByRole('button', { name: 'add' }))
    await advanceTime(30000)
    await advanceTime(650)
    expect(screen.getByRole('button', { name: 'Drill again' })).toBeInTheDocument()
    expect(screen.queryByRole('region', { name: 'Your flight review' })).not.toBeInTheDocument()
    expect(screen.getByRole('region', { name: 'Stage files' })).toHaveFocus()
    expect(drillsApi.reportSession).toHaveBeenCalledExactlyOnceWith(51, expect.objectContaining({ answers_total: 3, answers_correct: 3, completed: true }))
  })

  it('automatically ends a checkpoint fall and includes the attempted block order in the review', async () => {
    mount()
    await reachCheckpoint()
    fireEvent.click(screen.getByRole('button', { name: 'add' }))
    fireEvent.click(screen.getByRole('button', { name: 'git' }))
    await advanceTime(30000)
    await advanceTime(1600)
    expect(screen.getByText(/Blue fell through a gap/)).toBeInTheDocument()
    const review = screen.getByRole('region', { name: 'Your flight review' })
    expect(within(review).getByText('add git')).toBeInTheDocument()
    expect(within(review).getByText('git add')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Drill again' }))
    expect(screen.getByLabelText('3 of 3 lives remaining')).toBeInTheDocument()
  })

  it('cancels a pending transition when the session unmounts', async () => {
    const view = mount()
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    view.unmount()
    await advanceTime(2000)
    expect(drillsApi.saveRun).not.toHaveBeenCalled()
    expect(drillsApi.reportSession).not.toHaveBeenCalled()
  })

  it('pauses and resumes the current flight with Escape without leaving the drill', () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: 'Take off' }))
    const actor = document.querySelector('.drill-flight-actor')
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.getByRole('heading', { name: 'Flight paused' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Fly to answer \d: git add$/ })).toBeDisabled()
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/drill/51')
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('heading', { name: 'Flight paused' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Fly to answer \d: git add$/ })).toBeEnabled()
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    expect(document.querySelector('.drill-flight-actor')).toBe(actor)
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/drill/51')
  })

  it('does not toggle pause when Escape repeats while the key is held', () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: 'Take off' }))
    fireEvent.keyDown(window, { key: 'Escape', repeat: true })
    expect(screen.queryByRole('heading', { name: 'Flight paused' })).not.toBeInTheDocument()
    fireEvent.keyDown(window, { key: 'Escape' })
    fireEvent.keyDown(window, { key: 'Escape', repeat: true })
    fireEvent.keyDown(window, { key: 'Escape', repeat: true })
    expect(screen.getByRole('heading', { name: 'Flight paused' })).toBeInTheDocument()
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/drill/51')
  })

  it('holds a hit and its automatic transition while paused, then advances once after resuming', async () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    await advanceTime(200)
    fireEvent.keyDown(window, { key: 'Escape' })
    await advanceTime(10000)
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Correct' })).toBeDisabled()
    expect(drillsApi.saveRun).not.toHaveBeenCalled()
    fireEvent.keyDown(window, { key: 'Escape' })
    await advanceTime(650)
    expect(screen.getByRole('heading', { name: 'Fill the missing piece.' })).toBeInTheDocument()
    expect(drillsApi.saveRun).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/drill/51')
  })

  it('keeps the X control as an explicit route back to the level map', () => {
    mount()
    const leave = screen.getByRole('link', { name: 'Leave the drill' })
    expect(leave).toHaveAttribute('href', '/stories/main')
    fireEvent.click(leave)
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/stories/main')
  })

  it('pauses a walking checkpoint with Escape before resuming the same crossing', async () => {
    mount()
    await reachCheckpoint()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.getByRole('heading', { name: 'Crossing paused' })).toBeInTheDocument()
    const actor = document.querySelector<HTMLElement>('.drill-path-actor')!
    const position = actor.style.transform
    await advanceTime(30000)
    expect(actor.style.transform).toBe(position)
    expect(screen.getByRole('heading', { name: 'Build the command.' })).toBeInTheDocument()
    expect(drillsApi.reportSession).not.toHaveBeenCalled()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.getByRole('button', { name: 'Pause crossing' })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'git' }))
    fireEvent.click(screen.getByRole('button', { name: 'add' }))
    await advanceTime(30000)
    await advanceTime(650)
    expect(screen.getByRole('button', { name: 'Drill again' })).toBeInTheDocument()
    expect(screen.getByTestId('drill-location')).toHaveTextContent('/drill/51')
  })
})
