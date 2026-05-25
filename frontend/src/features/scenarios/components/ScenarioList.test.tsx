import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ScenarioList } from './ScenarioList'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'

vi.mock('@/features/scenarios/api/scenariosApi', () => ({
  scenariosApi: {
    listForLesson: vi.fn(),
    listForModule: vi.fn(),
    startSession: vi.fn(),
    retrySession: vi.fn(),
  },
}))

vi.mock('@/features/review/api/reviewApi', () => ({
  reviewApi: {
    startReviewSession: vi.fn(),
  },
}))

vi.mock('@/features/scenarios/components/SkillFocusPreviewModal', () => ({
  SkillFocusPreviewModal: ({ onProceed }: { onProceed?: () => void }) => (
    <div role="dialog">
      Command preview modal
      {onProceed ? <button type="button" onClick={onProceed}>Proceed</button> : null}
    </div>
  ),
}))

vi.mock('@/features/scenarios/utils/scenarioCache', () => ({
  invalidateScenarioProgressQueries: vi.fn(),
  syncScenarioSessionInCache: vi.fn(),
}))

const baseDifficulty: DifficultyAccess = {
  id: 10,
  difficulty: 'easy',
  completion_type: 'state_based',
  status: 'not_started',
  review_available: false,
  mastery_progress: { mastered: 0, required: 1 },
  active_session_id: null,
  retry_session_id: null,
  policy: { id: 1, min_counted_commands: 1, max_counted_commands: 3 },
  completion: null,
  latest_attempt: null,
}

function difficulty(overrides: Partial<DifficultyAccess>): DifficultyAccess {
  return { ...baseDifficulty, ...overrides }
}

const scenario: ScenarioSkillFocus = {
  id: 1,
  slug: 'first-scenario',
  title: 'First scenario',
  focus: 'git status',
  summary: 'Read repository state.',
  skill_focus_type: 'command_specific',
  primary_focus_commands: ['git status'],
  learning_unit_id: 1,
  lesson_id: 1,
  difficulties: [
    difficulty({ id: 10, difficulty: 'easy' }),
    difficulty({ id: 20, difficulty: 'medium' }),
    difficulty({ id: 30, difficulty: 'hard' }),
  ],
}

const sessionResponse = {
  id: 99,
  module: { id: 1 },
  scenario: { id: 1 },
}

function renderList(items: ScenarioSkillFocus[] = [scenario]) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.mocked(scenariosApi.listForLesson).mockResolvedValue(items)
  vi.mocked(scenariosApi.startSession).mockResolvedValue(sessionResponse as never)
  vi.mocked(scenariosApi.retrySession).mockResolvedValue(sessionResponse as never)
  vi.spyOn(window, 'open').mockReturnValue(null)

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ScenarioList scope="lesson" lessonId={1} source="lesson" />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

async function expandScenario() {
  fireEvent.click(await screen.findByLabelText(/expand scenario 1/i))
}

describe('ScenarioList preview gate', () => {
  afterEach(() => {
    cleanup()
    localStorage.clear()
    vi.restoreAllMocks()
    vi.clearAllMocks()
  })

  it('opens command preview before the first Easy start', async () => {
    renderList()
    await expandScenario()

    fireEvent.click(screen.getAllByRole('button', { name: /start/i })[0])

    expect(await screen.findByRole('dialog')).toHaveTextContent('Command preview modal')
    expect(scenariosApi.startSession).not.toHaveBeenCalled()
  })

  it('does not automatically reopen the first-start preview after it has been seen', async () => {
    renderList()
    await expandScenario()

    fireEvent.click(screen.getAllByRole('button', { name: /start/i })[0])
    fireEvent.click(await screen.findByRole('button', { name: /proceed/i }))

    await waitFor(() => expect(scenariosApi.startSession).toHaveBeenCalledWith({
      difficulty_instance_id: 10,
      source_entry_point: 'lesson',
    }))

    cleanup()
    vi.clearAllMocks()
    renderList()
    await expandScenario()
    fireEvent.click(screen.getAllByRole('button', { name: /start/i })[0])

    await waitFor(() => expect(scenariosApi.startSession).toHaveBeenCalledWith({
      difficulty_instance_id: 10,
      source_entry_point: 'lesson',
    }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('opens command preview from the scenario-level view button without starting a session', async () => {
    renderList()

    fireEvent.click(await screen.findByRole('button', { name: /view/i }))

    expect(await screen.findByRole('dialog')).toHaveTextContent('Command preview modal')
    expect(scenariosApi.startSession).not.toHaveBeenCalled()
  })

  it('starts Medium and Hard directly without opening preview', async () => {
    renderList()
    await expandScenario()

    const startButtons = screen.getAllByRole('button', { name: /start/i })
    fireEvent.click(startButtons[1])

    await waitFor(() => expect(scenariosApi.startSession).toHaveBeenCalledWith({
      difficulty_instance_id: 20,
      source_entry_point: 'lesson',
    }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()

    fireEvent.click(startButtons[2])
    await waitFor(() => expect(scenariosApi.startSession).toHaveBeenCalledWith({
      difficulty_instance_id: 30,
      source_entry_point: 'lesson',
    }))
  })

  it('retries Easy directly after a prior attempt', async () => {
    renderList([
      {
        ...scenario,
        difficulties: [
          difficulty({
            id: 10,
            difficulty: 'easy',
            status: 'failed',
            retry_session_id: 77,
            latest_attempt: {
              id: 77,
              status: 'failed',
              accuracy_rate: 0,
              command_accurate: null,
              counted_action_total: 2,
              total_attempts: 2,
              completed_at: null,
              ended_at: null,
            },
          }),
        ],
      },
    ])
    await expandScenario()

    fireEvent.click(screen.getByRole('button', { name: /retry/i }))

    await waitFor(() => expect(scenariosApi.retrySession).toHaveBeenCalledWith(77))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('renders diagnostic lessons with no playable difficulties as preview-only cards', async () => {
    renderList([
      {
        ...scenario,
        skill_focus_type: 'concept_specific',
        difficulties: [],
      },
    ])
    fireEvent.click(await screen.findByLabelText(/expand command preview/i))

    expect(screen.getByText('Command preview')).toBeInTheDocument()
    expect(screen.queryByText('Scenario 1')).not.toBeInTheDocument()
    expect(screen.getByText('Command preview only')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /^start$/i })).not.toBeInTheDocument()

    fireEvent.click(screen.getAllByRole('button', { name: /view/i })[0])
    expect(await screen.findByRole('dialog')).toHaveTextContent('Command preview modal')
    expect(scenariosApi.startSession).not.toHaveBeenCalled()
  })
})
