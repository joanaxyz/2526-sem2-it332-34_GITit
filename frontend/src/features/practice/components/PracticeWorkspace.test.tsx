import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen } from '@testing-library/react'
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
  ScenarioStatusHeader: () => <div>Scenario status header</div>,
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
  ProjectStructurePanel: () => <div>Project structure panel</div>,
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
    task_prompt: '',
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
    non_counted_diagnostic_total: 0,
    remaining_counted_commands: 3,
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
  vi.mocked(useCommandSubmission).mockReturnValue({
    isPending: false,
    mutate: vi.fn(),
  } as unknown as ReturnType<typeof useCommandSubmission>)
  vi.mocked(useScenarioSession).mockReturnValue({
    query: { isLoading: false, isError: false },
    session,
    setSession: vi.fn(),
    lines: [],
    setLines: vi.fn(),
    feedback: '',
    setFeedback: vi.fn(),
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

  it('renders only the command-preview panels for inspection sessions', () => {
    renderWorkspace({ ...baseSession, completion_type: 'inspection' })

    expect(screen.getByText('Inspect the repository')).toBeInTheDocument()
    expect(screen.getByText('Variant A')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /view command preview/i })).toBeInTheDocument()
    expect(screen.getByText('Terminal panel')).toBeInTheDocument()
    expect(screen.getByText('Live DAG panel')).toBeInTheDocument()
    expect(screen.queryByText('Scenario status header')).not.toBeInTheDocument()
    expect(screen.queryByText('Scenario context panel')).not.toBeInTheDocument()
    expect(screen.queryByText('Expected state panel')).not.toBeInTheDocument()
    expect(screen.queryByText('Contextual feedback panel')).not.toBeInTheDocument()
    expect(screen.queryByText('Project structure panel')).not.toBeInTheDocument()
  })

  it('keeps the full workspace for state-based sessions', () => {
    renderWorkspace(baseSession)

    expect(screen.getByText('Scenario status header')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /preview/i })).toBeInTheDocument()
    expect(screen.getByText('Scenario context panel')).toBeInTheDocument()
    expect(screen.getByText('Expected state panel')).toBeInTheDocument()
    expect(screen.getByText('Contextual feedback panel')).toBeInTheDocument()
    expect(screen.getByText('Project structure panel')).toBeInTheDocument()
    expect(screen.getByText('Terminal panel')).toBeInTheDocument()
    expect(screen.getByText('Live DAG panel')).toBeInTheDocument()
  })
})
