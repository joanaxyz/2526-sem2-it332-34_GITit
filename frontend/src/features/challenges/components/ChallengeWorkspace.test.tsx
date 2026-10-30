import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeRun } from '@/features/challenges/types'

import { ChallengeWorkspace } from './ChallengeWorkspace'

const mocks = vi.hoisted(() => ({
  run: null as ChallengeRun | null,
  submit: vi.fn(),
  battleResolve: vi.fn(),
}))

vi.mock('@/features/challenges/hooks/useChallengeRun', () => ({
  useChallengeRun: () => ({ query: { isLoading: false, isError: false }, run: mocks.run, lines: [] }),
}))
vi.mock('@/features/challenges/hooks/useChallengeRunAssets', () => ({ useChallengeRunAssets: () => true }))
vi.mock('@/features/challenges/hooks/useChallengeCommandSubmission', () => ({
  useChallengeCommandSubmission: () => ({ isPending: false, mutate: mocks.submit }),
}))
vi.mock('@/features/challenges/scaffolding/useScaffolding', () => ({
  useScaffolding: () => ({ clearToast: vi.fn(), evaluateAndNotify: vi.fn() }),
}))
vi.mock('@/features/challenges/hooks/useChallengeWorkspaceMutations', () => ({
  useChallengeWorkspaceMutations: () => {
    const idle = { isPending: false, mutate: vi.fn(), mutateAsync: vi.fn() }
    return {
      exitMutation: idle, startLevelMutation: idle, replayMutation: idle, retryMutation: idle,
      createFileMutation: idle, writeFileMutation: idle, renameFileMutation: idle, deleteFileMutation: idle,
      startFreshAttempt: vi.fn(), playAgain: vi.fn(),
    }
  },
}))
vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({
  usePlayerLoadout: () => ({ companionSlug: 'blue', isLoading: false }),
}))
vi.mock('@/shared/battle/hooks/useBattleDirector', () => ({
  useBattleDirector: () => ({
    animating: false,
    onAttackStart: vi.fn(),
    currentMonsters: () => [],
    onResolve: mocks.battleResolve,
    onError: vi.fn(),
  }),
}))
// Canvas-heavy leaves; the layout around them stays real.
vi.mock('@/shared/level/workspace/WorkspaceBattlePanel', () => ({
  WorkspaceBattlePanel: () => <div data-testid="battle-stage" />,
}))
vi.mock('@/shared/level/components/LiveDagPanel', () => ({
  LiveDagPanel: ({ title }: { title: string }) => <div data-testid="dag-panel">{title}</div>,
}))
vi.mock('@/shared/level/components/ProjectStructurePanel', () => ({
  ProjectStructurePanel: () => <div data-testid="project-files" />,
}))
vi.mock('@/features/challenges/components/ChallengeOutcomeModal', () => ({ ChallengeOutcomeModal: () => null }))

const snapshot = {
  repository_initialized: true,
  commits: [{ id: 'c1', message: 'Start', parents: [], tree: {} }],
  branches: { main: 'c1' },
  head: { type: 'branch', name: 'main' },
  staging: {},
  working_tree: {},
  conflicts: [],
}

function challengeRun(): ChallengeRun {
  return {
    id: 9,
    status: 'started',
    replay: false,
    stars: 0,
    difficulty: 'easy',
    reward_coins: 50,
    challenge: { id: 2, slug: 'module-3-challenge-gate', title: 'Conflict Gate', summary: '', narrative: '', level_id: 31 },
    chapter: { id: 4, number: 3, title: 'Conflicts' },
    story: { id: 1, slug: 'arcane-spire', title: 'Arcane Spire', world_slug: 'arcane-spire' },
    variant: { id: 77, label: 'Merge the banner, then backport the checkout fix' },
    mastery_progress: { cleared: false, stars: 0 },
    policy: { min_counted_commands: 5, max_counted_commands: 12 },
    counts: {
      counted_action_total: 0, minimum_counted_commands: 5, maximum_counted_commands: 12,
      non_counted_diagnostic_total: 0, remaining_counted_commands: 12, max_reached: false, total_attempts: 0,
    },
    scaffolding: { live_dag: true, expected_state: true, contextual_feedback: true },
    scenario_context: {
      schema_version: 3,
      story: 'Sage has decided on the final wording.',
      task: 'Merge `feature/banner`, then copy the fix to `release/1.4`.',
      objective_checks: ['main has a merge commit with feature/banner as a parent.'],
    },
    repository_state: snapshot,
    expected_state: snapshot,
    visualization: {},
    steps: [],
    next_difficulty: null,
    sibling_levels: [],
    completion: null,
  } as unknown as ChallengeRun
}

function renderWorkspace() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const router = createMemoryRouter(
    [{ path: '/challenge-runs/:runId', element: <ChallengeWorkspace /> }],
    { initialEntries: ['/challenge-runs/9'] },
  )
  render(<QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider>)
}

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
  mocks.run = null
  window.localStorage.clear()
})

describe('ChallengeWorkspace', () => {
  it('plays a gate trial in the adventure workspace: battle, terminal, diagrams and objectives', () => {
    mocks.run = challengeRun()
    renderWorkspace()

    // The briefing opens first, as it does for an adventure tier.
    const briefing = screen.getByRole('dialog')
    expect(within(briefing).getByText('Merge the banner, then backport the checkout fix', { selector: 'p' })).toBeInTheDocument()
    fireEvent.keyDown(briefing, { key: 'Escape' })

    expect(screen.getByTestId('battle-stage')).toBeInTheDocument()
    expect(screen.getByTestId('tier-terminal-stage')).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Live' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Expected' })).toBeInTheDocument()
    expect(screen.getByRole('list', { name: 'Objectives' })).toHaveTextContent('main has a merge commit')
    expect(screen.getByTestId('tier-feedback-region')).toBeInTheDocument()

    const status = screen.getByRole('group', { name: 'Level status' })
    expect(status).toHaveTextContent('Challenge Gate')
    expect(status).toHaveTextContent('0 / 12')
    expect(status).toHaveTextContent('+50 GitCoins')
    expect(screen.queryByRole('separator')).not.toBeInTheDocument()
  })

  it('plays each command on the battle stage', () => {
    mocks.run = challengeRun()
    mocks.submit.mockImplementation((_command, options) => options.onSuccess({
      run: mocks.run,
      command_family: 'merge',
      command_outcome: { processed: true, command_family: 'merge', solved: false, rules_delta: 1 },
      step: { command_classification: 'git' },
    }))
    renderWorkspace()
    fireEvent.keyDown(screen.getByRole('dialog'), { key: 'Escape' })

    const input = screen.getByLabelText('Git command')
    fireEvent.change(input, { target: { value: 'git merge feature/banner' } })
    fireEvent.submit(input.closest('form')!)

    expect(mocks.submit).toHaveBeenCalledOnce()
    expect(mocks.battleResolve).toHaveBeenCalled()
  })
})
