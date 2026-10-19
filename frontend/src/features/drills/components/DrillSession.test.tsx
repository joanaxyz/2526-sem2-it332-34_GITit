import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { DrillSession } from './DrillSession'
import type { DrillPlan } from '@/features/drills/types'
import { useAuthStore } from '@/shared/auth/useAuth'

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
function mount() {
  client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  return render(<QueryClientProvider client={client}><MemoryRouter><DrillSession plan={plan} /></MemoryRouter></QueryClientProvider>)
}
async function advanceTime(ms: number) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms) })
}

describe('flight session with learner-paced questions', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('matchMedia', () => ({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() }))
    useAuthStore.getState().setSession('learner-token', { id: 1, username: 'learner', email: 'learner@example.com', is_staff: false })
  })
  afterEach(() => { cleanup(); client?.clear(); vi.useRealTimers(); vi.unstubAllGlobals() })

  it('keeps correct feedback visible until Continue serves the next question in the same arena', async () => {
    mount()
    const actor = document.querySelector('.drill-flight-actor')
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    expect(screen.getByRole('button', { name: 'Correct' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Continue' })).toHaveFocus()
    await advanceTime(10000)
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Correct' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(screen.getByRole('heading', { name: 'Fill the missing piece.' })).toBeInTheDocument()
    expect(document.querySelector('.drill-flight-actor')).toBe(actor)
    expect(screen.getByLabelText('3 of 3 lives remaining')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument()
  })

  it('waits for Continue after wrong hits and View results after the last life', async () => {
    mount()
    for (let lives = 2; lives >= 0; lives--) {
      fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git status$/ }))
      expect(screen.getByRole('button', { name: 'Wrong' })).toBeInTheDocument()
      expect(screen.getByLabelText(`${lives} of 3 lives remaining`)).toBeInTheDocument()
      if (lives > 0) {
        expect(screen.getByTestId('pose')).toHaveTextContent('float')
        await advanceTime(10000)
        expect(screen.getByRole('button', { name: 'Wrong' })).toBeDisabled()
        fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
      }
    }
    expect(screen.getByTestId('pose')).toHaveTextContent('die')
    await advanceTime(10000)
    expect(screen.getByTestId('pose')).toHaveTextContent('die')
    expect(screen.queryByRole('button', { name: 'Drill again' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'View results' })).toHaveFocus()
    fireEvent.click(screen.getByRole('button', { name: 'View results' }))
    expect(screen.getByRole('button', { name: 'Drill again' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Continue' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Drill again' }))
    expect(screen.getByLabelText('3 of 3 lives remaining')).toBeInTheDocument()
  })

  it('supports Enter to continue and ignores a held Enter key', () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    const continueButton = screen.getByRole('button', { name: 'Continue' })
    expect(fireEvent.keyDown(continueButton, { key: 'Enter', repeat: true })).toBe(false)
    expect(screen.getByRole('heading', { name: 'Which command does this?' })).toBeInTheDocument()
    fireEvent.keyDown(window, { key: 'Enter' })
    expect(screen.getByRole('heading', { name: 'Fill the missing piece.' })).toBeInTheDocument()
  })

  it('waits for Continue after checking an assembled answer before opening the summary', async () => {
    mount()
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: git add$/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.click(screen.getByRole('button', { name: /Fly to answer \d: add$/ }))
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.click(screen.getByRole('button', { name: 'git' }))
    fireEvent.click(screen.getByRole('button', { name: 'add' }))
    fireEvent.click(screen.getByRole('button', { name: 'Check' }))
    expect(screen.getByRole('button', { name: 'Continue' })).toHaveFocus()
    await advanceTime(10000)
    expect(screen.getByRole('heading', { name: 'Build the command.' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Drill again' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(screen.getByRole('button', { name: 'Drill again' })).toBeInTheDocument()
  })
})
