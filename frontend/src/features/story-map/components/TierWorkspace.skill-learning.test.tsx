import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { TierCommandResponse, TierRun } from './tierWorkspaceTypes'
import { TierWorkspace } from './TierWorkspace'

const mocks = vi.hoisted(() => ({ run: null as TierRun | null, submit: vi.fn(), finishAnimation: vi.fn() }))

vi.mock('@/features/story-map/hooks/useTierRun', () => ({ useTierRun: () => ({ query: { isLoading: false, isError: false }, run: mocks.run, lines: [] }) }))
vi.mock('@/features/story-map/hooks/useTierRunAssets', () => ({ useTierRunAssets: () => true }))
vi.mock('@/features/story-map/hooks/useTierCommandSubmission', () => ({ useTierCommandSubmission: () => ({ isPending: false, mutate: mocks.submit }) }))
vi.mock('@/features/story-map/scaffolding/useTierScaffolding', () => ({ useTierScaffolding: () => ({ clearToast: vi.fn(), evaluateAndNotify: vi.fn() }) }))
vi.mock('@/features/story-map/hooks/useLeaveAbandonedRun', () => ({ useLeaveAbandonedRun: vi.fn() }))
vi.mock('@/shared/tutoring/GuideTutor', () => ({ GuideTutor: ({ teachingKey }: { teachingKey: string }) => <div data-testid="guide-ai" data-teaching-key={teachingKey} /> }))
vi.mock('@/shared/level/workspace/useWorkspaceAutoOpen', () => ({ useWorkspaceAutoOpen: () => ({ storyOpen: false, tourOpen: false, guideAllowed: true }) }))
vi.mock('@/shared/level/workspace/useRepoGraphDrawer', () => ({ useRepoGraphDrawer: () => ({ drawerMode: false }) }))
vi.mock('@/shared/level/workspace/workspaceStory', () => ({ workspaceStoryContent: () => ({}) }))
vi.mock('@/shared/player-loadout/usePlayerLoadout', () => ({ usePlayerLoadout: () => ({ companionSlug: 'blue', isLoading: false }) }))
vi.mock('@/shared/level/workspace/useDagAnimation', () => ({ useDagAnimation: () => ({ animating: false, onCommandStart: vi.fn(), onCommandResolved: vi.fn(), onCommandError: vi.fn() }) }))
vi.mock('@/shared/battle/hooks/useBattleDirector', async () => {
  const { useState } = await import('react')
  return {
    useBattleDirector: () => {
      const [animating, setAnimating] = useState(false)
      mocks.finishAnimation.mockImplementation(() => setAnimating(false))
      return { animating, onAttackStart: vi.fn(), currentMonsters: () => [], onResolve: () => setAnimating(true), onError: vi.fn() }
    },
  }
})
vi.mock('@/features/story-map/hooks/useTierWorkspaceMutations', () => ({
  useTierWorkspaceMutations: () => {
    const idle = { isPending: false, mutate: vi.fn(), mutateAsync: vi.fn() }
    return { exitMutation: idle, startLevelMutation: idle, continueMutation: idle, replayMutation: idle, retryMutation: idle, createFileMutation: idle, writeFileMutation: idle, renameFileMutation: idle, deleteFileMutation: idle }
  },
}))
vi.mock('@/features/story-map/components/TierStatusHeader', () => ({ TierStatusHeader: () => null }))
vi.mock('@/features/story-map/components/tier-workspace/TierStatsBar', () => ({ TierStatsBar: () => null }))
vi.mock('@/shared/level/workspace/GameplayWorkspaceMain', () => ({
  GameplayWorkspaceMain: ({ onCommand }: { onCommand: (command: string) => void }) => <button onClick={() => onCommand('git init')}>Run git init</button>,
}))
vi.mock('@/features/story-map/components/CommandIntroductionPanel', () => ({ CommandIntroductionPanel: () => <div role="dialog" aria-label="Next command introduction" /> }))
vi.mock('@/features/story-map/components/TierOutcomeModal', () => ({ TierOutcomeModal: ({ open }: { open: boolean }) => open ? <div role="dialog" aria-label="Level complete" /> : null }))
vi.mock('@/shared/level/workspace/WorkspaceStoryModal', () => ({ WorkspaceStoryModal: () => null }))
vi.mock('@/shared/level/workspace/ExitConfirmModal', () => ({ ExitConfirmModal: () => null }))
vi.mock('@/shared/level/workspace/StartOverConfirmModal', () => ({ StartOverConfirmModal: () => null }))

const run = { id: 1, status: 'started', tier: { id: 1, adventure_level_id: 1, difficulty: 'easy' }, scaffolding: {}, repository_state: {}, replay: false, tutor: null, command_guides: [], guide_elsewhere: null, tips: [] } as unknown as TierRun
const skill = { id: 7, slug: 'git-init', title: 'Create a repository', base_command: 'git init', summary: '', chapter_number: 1, chapter_title: 'Foundations' }

function renderWorkspace() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const router = createMemoryRouter([{ path: '/tier-runs/:runId', element: <TierWorkspace /> }], { initialEntries: ['/tier-runs/1'] })
  render(<QueryClientProvider client={queryClient}><RouterProvider router={router} /></QueryClientProvider>)
}

afterEach(() => { cleanup(); vi.clearAllMocks(); mocks.run = null; window.localStorage.clear() })

describe('TierWorkspace learned-skill events', () => {
  it.each(['introduction', 'outcome'] as const)('waits for battle resolution and gives the earned skill priority over the next %s', async (next) => {
    mocks.run = run
    mocks.submit.mockImplementation((_command, options) => {
      const nextRun = { ...run, status: next === 'outcome' ? 'completed' : 'started', tutor: next === 'introduction' ? { phase: 'introduction', teaching_key: 'git-add', context_id: '2', command_form: { usage_form: 'git add <path>' }, help_token: 'signed' } : null } as TierRun
      mocks.run = nextRun
      options.onSuccess({ run: nextRun, command_family: 'init', command_outcome: { processed: true, command_family: 'init', solved: next === 'outcome' }, step: { command_classification: 'git' }, learned_skills: [skill] } as unknown as TierCommandResponse)
    })
    renderWorkspace()
    fireEvent.click(screen.getByRole('button', { name: 'Run git init' }))
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    act(() => mocks.finishAnimation())
    const reveal = await screen.findByRole('dialog', { name: "You've learned a new skill" })
    expect(screen.queryByRole('dialog', { name: 'Next command introduction' })).not.toBeInTheDocument()
    expect(screen.queryByRole('dialog', { name: 'Level complete' })).not.toBeInTheDocument()
    fireEvent.click(within(reveal).getByRole('img', { name: 'Create a repository skill' }))
    expect(screen.getByRole('dialog', { name: next === 'outcome' ? 'Level complete' : 'Next command introduction' })).toBeInTheDocument()
  })

  it.each([[], undefined])('does not infer learning from a successful command without an event (%j)', (learnedSkills) => {
    mocks.run = run
    mocks.submit.mockImplementation((_command, options) => options.onSuccess({ run, command_family: 'init', command_outcome: { processed: true, command_family: 'init', solved: false }, step: { command_classification: 'git' }, learned_skills: learnedSkills } as unknown as TierCommandResponse))
    renderWorkspace()
    fireEvent.click(screen.getByRole('button', { name: 'Run git init' }))
    act(() => mocks.finishAnimation())
    expect(screen.queryByRole('dialog', { name: "You've learned a new skill" })).not.toBeInTheDocument()
  })
})

describe('TierWorkspace guide chat', () => {
  it('keeps the AI launcher apart from the guide, about the latest guide while it is collapsed', () => {
    mocks.run = {
      ...run,
      command_guides: [{ teaching_key: 'git-init/current-directory', command_form: { usage_form: 'git init' }, help_token: 'signed' }],
    } as unknown as TierRun
    renderWorkspace()
    expect(screen.queryByRole('dialog', { name: 'Next command introduction' })).not.toBeInTheDocument()
    expect(screen.getByTestId('guide-ai')).toHaveAttribute('data-teaching-key', 'git-init/current-directory')
  })

  it('has no AI launcher when the run has no guide to talk about', () => {
    mocks.run = run
    renderWorkspace()
    expect(screen.queryByTestId('guide-ai')).not.toBeInTheDocument()
  })
})
