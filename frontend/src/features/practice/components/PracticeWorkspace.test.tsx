import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import { PracticeWorkspace } from './PracticeWorkspace'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import { useCommandSubmission } from '@/features/practice/hooks/useCommandSubmission'
import { useScenarioSession } from '@/features/practice/hooks/useScenarioSession'

vi.mock('@/features/practice/hooks/useScenarioSession', () => ({
  useScenarioSession: vi.fn(),
}))

vi.mock('@/features/practice/hooks/useCommandSubmission', () => ({
  useCommandSubmission: vi.fn(),
}))

vi.mock('@/features/auth/hooks/useAuth', () => ({
  useAuthStore: vi.fn((selector: (state: { user: null }) => unknown) => selector({ user: null })),
}))

vi.mock('@/features/practice/utils/scenarioTour', () => ({
  hasSeenScenarioTour: vi.fn(() => true),
  markScenarioTourSeen: vi.fn(),
}))

vi.mock('@/features/scenarios/api/scenariosApi', () => ({
  scenariosApi: {
    abandonSession: vi.fn(),
    getSkillFocus: vi.fn(),
    listForModule: vi.fn(),
    retrySession: vi.fn(),
    startSession: vi.fn(),
    submitDemoCommand: vi.fn(),
  },
}))

vi.mock('@/features/review/api/reviewApi', () => ({
  reviewApi: {
    startReviewSession: vi.fn(),
  },
}))

vi.mock('@/features/scenarios/components/ScenarioStatusHeader', () => ({
  ScenarioStatusHeader: ({
    onStartOver,
    onRetry,
  }: {
    onStartOver?: () => void
    onRetry?: () => void
  }) => (
    <div>
      Scenario status header
      {onStartOver ? (
        <button type="button" onClick={onStartOver}>
          Start over
        </button>
      ) : null}
      {onRetry ? (
        <button type="button" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  ),
}))

vi.mock('@/features/scenarios/components/ScenarioContextPanel', () => ({
  ScenarioContextPanel: () => <div>Scenario context panel</div>,
}))

vi.mock('@/features/practice/components/ExpectedStatePanel', () => ({
  ExpectedStatePanel: () => <div>Expected state panel</div>,
}))

vi.mock('@/features/practice/components/ContextualFeedbackPanel', () => ({
  ContextualFeedbackPanel: () => <div>Contextual feedback panel</div>,
}))

vi.mock('@/features/practice/components/ProjectStructurePanel', () => ({
  ProjectStructurePanel: ({ className }: { className?: string }) => (
    <div data-testid="project-structure-panel" className={className}>
      Project structure panel
    </div>
  ),
}))

vi.mock('@/features/practice/components/LiveDagPanel', () => ({
  LiveDagPanel: () => <div>Live DAG panel</div>,
}))

vi.mock('@/features/practice/components/TerminalPanel', () => ({
  TerminalPanel: () => <div>Terminal panel</div>,
}))

vi.mock('@/features/practice/components/CompletionCelebrationModal', () => ({
  CompletionCelebrationModal: ({ open }: { open: boolean }) => (open ? <div>Completion modal</div> : null),
}))

vi.mock('@/features/practice/components/ScenarioWorkspaceTour', () => ({
  ScenarioWorkspaceTour: () => <div>Workspace tour</div>,
}))

const repositoryState = {
  commits: [],
  branches: { main: null },
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const baseSession: ScenarioSession = {
  id: 42,
  mode: 'primary',
  status: 'started',
  difficulty_instance_id: 7,
  completed_at: null,
  first_attempt_star_eligible: true,
  completion_type: 'state_based',
  scenario: {
    id: 5,
    slug: 'inspect-state',
    title: 'Inspect the repository',
    focus: 'git status',
    narrative: '',
  },
  module: {
    id: 3,
    number: 1,
    title: 'Basics',
  },
  difficulty: 'easy',
  variant: {
    id: 9,
    label: 'Variant A',
    changed_variant: false,
  },
  mastery_progress: {
    mastered: 0,
    required: 3,
  },
  policy: {
    id: 11,
    min_counted_commands: 1,
    max_counted_commands: 3,
    non_counted_patterns: [],
  },
  counts: {
    counted_action_total: 0,
    minimum_counted_commands: 1,
    maximum_counted_commands: 3,
    non_counted_diagnostic_total: 0,
    remaining_counted_commands: 3,
    max_reached: false,
    total_attempts: 0,
  },
  scaffolding: {
    live_dag: true,
    expected_state: true,
    contextual_feedback: true,
  },
  repository_state: repositoryState,
  expected_state: repositoryState,
  steps: [],
  review_mode: false,
  next_difficulty: null,
  completion: null,
}

function renderWorkspace(session: ScenarioSession) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.mocked(scenariosApi.listForModule).mockResolvedValue([])
  vi.mocked(scenariosApi.retrySession).mockResolvedValue({ ...session, id: session.id + 1, variant: { ...session.variant, label: 'Variant B' } })
  vi.mocked(useCommandSubmission).mockReturnValue({
    isPending: false,
    mutate: vi.fn(),
  } as unknown as ReturnType<typeof useCommandSubmission>)
  vi.mocked(useScenarioSession).mockReturnValue({
    query: { isLoading: false, isError: false },
    session,
    lines: [],
    setLines: vi.fn(),
    feedback: '',
    resetLocalSessionState: vi.fn(),
  } as unknown as ReturnType<typeof useScenarioSession>)

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/practice/42']}>
        <Routes>
          <Route path="/practice/:sessionId" element={<PracticeWorkspace />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('PracticeWorkspace', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('keeps the full workspace for state-based sessions', () => {
    renderWorkspace(baseSession)

    expect(screen.getByText('Scenario status header')).toBeInTheDocument()
    expect(screen.getByText('Scenario context panel')).toBeInTheDocument()
    expect(screen.getByText('Expected state panel')).toBeInTheDocument()
    expect(screen.getByText('Contextual feedback panel')).toBeInTheDocument()
    expect(screen.getByText('Project structure panel')).toBeInTheDocument()
    expect(screen.getByText('Terminal panel')).toBeInTheDocument()
    expect(screen.getByText('Live DAG panel')).toBeInTheDocument()
  })

  it('splits long sidebar content from the project structure scroll region', () => {
    renderWorkspace(baseSession)

    expect(screen.getByTestId('workspace-sidebar')).toHaveClass('overflow-hidden')
    expect(screen.getByTestId('scenario-context-scroll')).toHaveClass('overflow-y-auto')
    expect(screen.getByTestId('project-structure-region')).toHaveClass('min-h-[14rem]')
    expect(screen.getByTestId('project-structure-panel')).toHaveClass('h-full')
  })

  it('confirms before retrying an active workspace as a fresh attempt', async () => {
    renderWorkspace(baseSession)

    fireEvent.click(screen.getByRole('button', { name: /start over/i }))

    expect(screen.getByRole('dialog', { name: /start fresh attempt/i })).toBeInTheDocument()
    expect(screen.getByText(/current workspace state resets/i)).toBeInTheDocument()
    expect(scenariosApi.retrySession).not.toHaveBeenCalled()

    fireEvent.click(screen.getByRole('button', { name: /start fresh attempt/i }))

    await waitFor(() => expect(scenariosApi.retrySession).toHaveBeenCalledWith(baseSession.id))
  })
})
