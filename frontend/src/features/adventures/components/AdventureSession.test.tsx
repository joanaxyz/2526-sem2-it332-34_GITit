import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { queryKeys } from '@/shared/api/queryKeys'
import type { AdventureRun } from '@/features/adventures/types'
import { AdventureSession } from './AdventureSession'

const mocks = vi.hoisted(() => ({
  useAdventureRun: vi.fn(),
  useStartAdventureRun: vi.fn(),
  discardRun: vi.fn(() => Promise.resolve()),
}))

vi.mock('@/features/adventures/hooks/useAdventureRun', () => ({
  useAdventureRun: mocks.useAdventureRun,
  useStartAdventureRun: mocks.useStartAdventureRun,
}))

vi.mock('@/features/adventures/api/adventuresApi', () => ({
  adventuresApi: {
    discardRun: mocks.discardRun,
  },
}))

vi.mock('@/shared/battle/hooks/useBattleDirector', () => ({
  useBattleDirector: () => ({
    defeated: false,
    playerHp: null,
    playerMaxHp: null,
    transitionCue: null,
    animating: false,
    stagedMonsterIds: new Set(),
    activeMonsterId: null,
    roster: [],
    bindPlayer: vi.fn(),
    bindBackdrop: vi.fn(),
    bindEffectLayer: vi.fn(),
    bindBackEffectLayer: vi.fn(),
    bindMonster: vi.fn(),
    currentMonsters: () => [],
    onAttackStart: vi.fn(),
    onResolve: vi.fn(),
    onError: vi.fn(),
    setEncounter: vi.fn(),
  }),
}))

vi.mock('@/features/adventures/components/AdventureBattlePanel', () => ({
  AdventureBattlePanel: () => <div data-testid="adventure-battle-panel" />,
}))

vi.mock('@/features/adventures/components/AdventureContextPanel', () => ({
  AdventureContextPanel: () => <div data-testid="adventure-context-panel" />,
}))

vi.mock('@/features/adventures/components/AdventureLevelLibraryModal', () => ({
  AdventureLevelLibraryModal: ({ onClose }: { onClose: () => void }) => (
    <div aria-label="Command Library" role="dialog">
      <button type="button" onClick={onClose}>
        Close library
      </button>
    </div>
  ),
}))

vi.mock('@/features/adventures/components/AdventureOutcomeModal', () => ({
  AdventureOutcomeModal: ({
    open,
    onRestart,
    isRestarting,
  }: {
    open: boolean
    onRestart: () => void
    isRestarting?: boolean
  }) =>
    open ? (
      <button type="button" disabled={isRestarting} onClick={onRestart}>
        {isRestarting ? 'Starting fresh run' : 'Try again'}
      </button>
    ) : null,
}))

vi.mock('@/shared/level/components/ProjectStructurePanel', () => ({
  ProjectStructurePanel: () => <div data-testid="project-structure-panel" />,
}))

vi.mock('@/shared/level/components/TerminalPanel', () => ({
  TerminalPanel: () => <div data-testid="terminal-panel" />,
}))

vi.mock('@/shared/level/components/WorkspaceEditorOverlay', () => ({
  WorkspaceEditorOverlay: () => null,
}))

const failedRun = {
  id: 101,
  status: 'failed',
  replay: false,
  stars: 0,
  library_opened: false,
  is_passed: false,
  selected_level: { id: 501, slug: 'create-repository', title: 'Create a repository', is_required: true },
  next_level: null,
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  chapter_id: 3,
  current_level_index: 1,
  total_levels: 1,
  current_wave: 1,
  total_waves: 1,
  mastery: {
    commands: [],
    commands_mastered: 0,
    total_commands: 1,
    total_achievable: 1,
    passed: false,
  },
  completed_at: null,
  current_attempt: {
    id: 201,
    order: 1,
    wave: 0,
    position: 0,
    status: 'failed',
    level: { id: 501, slug: 'create-repository', title: 'Create a repository', is_required: true },
    variant: { id: 1, label: 'Variant A' },
    scenario_context: {
      story: '',
      task: '',
      details: [],
    },
    objective_checks: [],
    scaffolding: {
      live_dag: false,
      expected_state: false,
      contextual_feedback: false,
    },
    command_budget: {
      min_counted_commands: 1,
      max_counted_commands: 3,
    },
    counts: {
      command_count: 3,
      counted_command_count: 3,
    },
    repository_state: {},
    steps: [],
  },
  results: [],
  progress: { completed: 0, total: 1 },
} as unknown as AdventureRun

const retryRun = {
  ...failedRun,
  id: 102,
  status: 'started',
  current_attempt: {
    ...failedRun.current_attempt!,
    id: 202,
    status: 'started',
    counts: {
      command_count: 0,
      counted_command_count: 0,
    },
  },
} as unknown as AdventureRun

function renderSession(queryClient: QueryClient) {
  const router = createMemoryRouter(
    [
      {
        path: '/adventure-runs/:runId',
        element: <AdventureSession runId={101} />,
      },
      {
        path: '/stories/:storySlug',
        element: <div>story map</div>,
      },
    ],
    { initialEntries: ['/adventure-runs/101'] },
  )

  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  )
}

describe('AdventureSession', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('starts retry runs in place so the battle transition can stay mounted', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    const restartMutation = {
      isPending: false,
      mutate: vi.fn((_variables, options?: { onSuccess?: (run: AdventureRun) => void }) => {
        options?.onSuccess?.(retryRun)
      }),
    }
    const nextLevelMutation = {
      isPending: false,
      mutate: vi.fn(),
    }
    let startHookCall = 0

    mocks.useAdventureRun.mockReturnValue({
      query: {
        isLoading: false,
        isError: false,
        data: failedRun,
      },
      lines: [],
      discardRun: { isPending: false, mutate: vi.fn() },
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    })
    mocks.useStartAdventureRun.mockImplementation(() => {
      startHookCall += 1
      return startHookCall % 2 === 1 ? restartMutation : nextLevelMutation
    })

    renderSession(queryClient)

    fireEvent.click(await screen.findByRole('button', { name: /try again/i }))

    await waitFor(() => {
      expect(restartMutation.mutate).toHaveBeenCalledWith(
        { levelId: failedRun.selected_level!.id },
        expect.objectContaining({ onSuccess: expect.any(Function) }),
      )
    })
    expect(nextLevelMutation.mutate).not.toHaveBeenCalled()
    expect(queryClient.getQueryData(queryKeys.adventureRun(retryRun.id))).toEqual(retryRun)
  })

  it('opens the command library from active adventure levels', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })

    mocks.useAdventureRun.mockReturnValue({
      query: {
        isLoading: false,
        isError: false,
        data: retryRun,
      },
      lines: [],
      discardRun: { isPending: false, mutate: vi.fn() },
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    })
    mocks.useStartAdventureRun.mockReturnValue({ isPending: false, mutate: vi.fn() })

    renderSession(queryClient)

    fireEvent.click(screen.getByRole('button', { name: /open the command guide/i }))

    expect(await screen.findByRole('dialog', { name: /command library/i })).toBeInTheDocument()
  })

  it('omits the static command guide and DAG from adventure runs', () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })

    mocks.useAdventureRun.mockReturnValue({
      query: {
        isLoading: false,
        isError: false,
        data: retryRun,
      },
      lines: [],
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    })
    mocks.useStartAdventureRun.mockReturnValue({ isPending: false, mutate: vi.fn() })

    renderSession(queryClient)

    expect(screen.getByTestId('terminal-panel')).toBeInTheDocument()
    expect(screen.queryByTestId('live-dag-panel')).not.toBeInTheDocument()
    expect(screen.queryByText(/run guide/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/reference commands/i)).not.toBeInTheDocument()
  })

  it('closes the exit dialog after starting a fresh adventure run', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    const restartMutation = {
      isPending: false,
      mutate: vi.fn((_variables, options?: { onSuccess?: (run: AdventureRun) => void }) => {
        options?.onSuccess?.({ ...retryRun, id: 103 } as AdventureRun)
      }),
    }

    mocks.useAdventureRun.mockReturnValue({
      query: {
        isLoading: false,
        isError: false,
        data: retryRun,
      },
      lines: [],
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    })
    mocks.useStartAdventureRun.mockReturnValue(restartMutation)

    renderSession(queryClient)

    fireEvent.click(screen.getByRole('button', { name: /^exit$/i }))
    const dialog = await screen.findByRole('dialog', { name: /exit adventure/i })
    fireEvent.click(within(dialog).getByRole('button', { name: /^retry$/i }))

    await waitFor(() => {
      expect(restartMutation.mutate).toHaveBeenCalled()
      expect(screen.queryByRole('dialog', { name: /exit adventure/i })).not.toBeInTheDocument()
    })
  })

  it('does not show the outcome modal when an active adventure is discarded on exit', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })
    mocks.useAdventureRun.mockImplementation(() => ({
      query: {
        isLoading: false,
        isError: false,
        data: retryRun,
      },
      lines: [],
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    }))
    mocks.useStartAdventureRun.mockReturnValue({ isPending: false, mutate: vi.fn() })

    renderSession(queryClient)

    fireEvent.click(screen.getByRole('button', { name: /^exit$/i }))
    const dialog = await screen.findByRole('dialog', { name: /exit adventure/i })
    fireEvent.click(within(dialog).getByRole('button', { name: /^exit$/i }))

    await waitFor(() => {
      expect(mocks.discardRun).toHaveBeenCalledWith(retryRun.id)
    })
    expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument()
  })

  it('keeps active adventure runs alive across browser refreshes', () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    })

    mocks.useAdventureRun.mockReturnValue({
      query: {
        isLoading: false,
        isError: false,
        data: retryRun,
      },
      lines: [],
      createFile: { isPending: false, mutateAsync: vi.fn() },
      writeFile: { isPending: false, mutateAsync: vi.fn() },
      renameFile: { isPending: false, mutateAsync: vi.fn() },
      deleteFile: { isPending: false, mutateAsync: vi.fn() },
    })
    mocks.useStartAdventureRun.mockReturnValue({ isPending: false, mutate: vi.fn() })

    renderSession(queryClient)

    fireEvent(window, new Event('pagehide'))

    expect(mocks.discardRun).not.toHaveBeenCalled()
  })
})
