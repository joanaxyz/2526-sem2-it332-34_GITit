import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactElement } from 'react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ChallengeTrialAccess } from '@/features/challenges/types'
import type {
  AdventureLevelSummary,
  AdventureLevelTierAccess,
  ChallengeSummary,
  LearningChapter,
} from '@/features/story-map/types'

import { StoryAdventurePath } from './StoryAdventurePath'

function renderPath(ui: ReactElement) {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

const mocks = vi.hoisted(() => ({
  openAdventureLevel: vi.fn(),
  openChallengeArtifact: vi.fn(),
}))

vi.mock('@/features/story-map/hooks/useStoryArtifactNavigation', () => ({
  useStoryArtifactNavigation: () => mocks,
}))

const chapter: LearningChapter = {
  adventure_level_count: 1,
  challenge_count: 1,
  chest_schedule: [],
  command_skill_count: 1,
  description: 'Learn the foundations.',
  id: 1,
  is_orientation: false,
  is_playable: true,
  level_completion: { denominator: 4, numerator: 1, value: 25 },
  lock_reason: '',
  locked: false,
  number: 1,
  slug: 'foundations',
  sort_order: 1,
  story: { id: 1, slug: 'arcane-spire', title: 'The Arcane Spire', world_slug: 'arcane-spire' },
  title: 'Foundations',
}

const adventure: AdventureLevelSummary = {
  item_type: 'adventure',
  id: 10,
  slug: 'initialize-repository',
  title: 'Initialize a Repository',
  description: '',
  command: 'git init',
  locked: false,
  lock_reason: '',
  completion: {
    stars: 3,
    counted_action_total: 1,
    completed_at: '2026-08-25T00:00:00Z',
  },
  is_passed: true,
  tiers: [],
}

function trial(
  id: number,
  difficulty: 'easy' | 'medium' | 'hard',
  status: ChallengeTrialAccess['status'],
): ChallengeTrialAccess {
  return {
    id,
    difficulty,
    status,
    cleared: false,
    replay_available: false,
    latest_attempt: null,
    completion: null,
    command_budget: {
      min_counted_commands: 1,
      max_counted_commands: 4,
    },
  }
}

const easyTrial = trial(21, 'easy', 'not_started')
const challenge: ChallengeSummary = {
  item_type: 'challenge',
  id: 20,
  slug: 'repository-foundations-gate',
  title: 'Repository Foundations Trial',
  summary: 'Prove the chapter skills.',
  narrative: 'The gate awaits.',
  status: 'not_started',
  completed: false,
  locked: false,
  trials: [easyTrial, trial(22, 'medium', 'locked'), trial(23, 'hard', 'locked')],
}

describe('StoryAdventurePath challenge gate', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('opens difficulty choices in a panel after the path instead of over its nodes', () => {
    const { container } = renderPath(
      <StoryAdventurePath
        chapter={chapter}
        levels={[adventure]}
        challenges={[challenge]}
        challengesLocked={false}
        loading={false}
      />,
    )

    const gate = screen.getByRole('button', { name: 'Challenge trials' })
    expect(gate).toHaveTextContent('Challenge Gate')
    fireEvent.click(gate)

    const panel = screen.getByRole('region', { name: 'Challenge Gate' })
    expect(panel.previousElementSibling).toHaveClass('story-path-canvas')
    expect(container.querySelector('.story-path-canvas .story-trials-panel')).not.toBeInTheDocument()
    expect(within(panel).getByText('0 / 3 cleared')).toBeInTheDocument()

    const easy = within(panel).getByRole('button', {
      name: 'Repository Foundations Trial: easy challenge trial',
    })
    expect(easy).toBeEnabled()
    expect(
      within(panel).getByRole('button', {
        name: 'Repository Foundations Trial: medium challenge trial',
      }),
    ).toBeDisabled()
    expect(
      within(panel).getByRole('button', {
        name: 'Repository Foundations Trial: hard challenge trial',
      }),
    ).toBeDisabled()

    fireEvent.click(easy)
    expect(mocks.openChallengeArtifact).toHaveBeenCalledWith(easyTrial, 'start')
  })

  it('closes the challenge panel with Escape', () => {
    renderPath(
      <StoryAdventurePath
        chapter={chapter}
        levels={[adventure]}
        challenges={[challenge]}
        challengesLocked={false}
        loading={false}
      />,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Challenge trials' }))
    expect(screen.getByRole('region', { name: 'Challenge Gate' })).toBeInTheDocument()

    fireEvent.keyDown(window, { key: 'Escape' })
    expect(screen.queryByRole('region', { name: 'Challenge Gate' })).not.toBeInTheDocument()
  })

  it('moves focus into the panel on open and restores it to the Challenge Gate button on close', async () => {
    renderPath(
      <StoryAdventurePath
        chapter={chapter}
        levels={[adventure]}
        challenges={[challenge]}
        challengesLocked={false}
        loading={false}
      />,
    )

    const gate = screen.getByRole('button', { name: 'Challenge trials' })
    gate.focus()
    fireEvent.click(gate)

    const panel = await screen.findByRole('region', { name: 'Challenge Gate' })
    const easyTrialCard = within(panel).getByRole('button', {
      name: 'Repository Foundations Trial: easy challenge trial',
    })
    await waitFor(() => expect(easyTrialCard).toHaveFocus())

    fireEvent.keyDown(window, { key: 'Escape' })

    expect(screen.queryByRole('region', { name: 'Challenge Gate' })).not.toBeInTheDocument()
    await waitFor(() => expect(gate).toHaveFocus())
  })
})

function tier(
  id: number,
  difficulty: AdventureLevelTierAccess['difficulty'],
  overrides: Partial<AdventureLevelTierAccess> = {},
): AdventureLevelTierAccess {
  return {
    id,
    difficulty,
    locked: false,
    wave_progress: { completed: 0, total: 2 },
    completion: null,
    ...overrides,
  }
}

const tieredLevel: AdventureLevelSummary = {
  ...adventure,
  id: 11,
  slug: 'stage-and-commit',
  title: 'Stage and Commit',
  description: 'Move work from the worktree into a commit that sticks.',
  completion: null,
  tiers: [
    tier(31, 'easy', {
      wave_progress: { completed: 1, total: 1 },
      completion: { stars: 3, counted_action_total: 1, completed_at: '2026-08-25T00:00:00Z' },
    }),
    tier(32, 'medium', { wave_progress: { completed: 1, total: 2 } }),
    tier(33, 'hard', { locked: true }),
  ],
}

describe('StoryAdventurePath level callout', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  function openCallout() {
    const result = renderPath(
      <StoryAdventurePath
        chapter={chapter}
        levels={[tieredLevel]}
        challenges={[challenge]}
        challengesLocked={false}
        loading={false}
      />,
    )
    const node = screen.getByRole('button', { name: /^Level 1: Stage and Commit\./ })
    node.focus()
    fireEvent.click(node)
    return { ...result, node }
  }

  it('marks exactly one tier as the next action and locks the rest', () => {
    openCallout()

    const callout = screen.getByRole('region', { name: 'Stage and Commit' })
    expect(within(callout).getByText('Level 01')).toBeInTheDocument()

    const cleared = within(callout).getByRole('button', {
      name: 'Stage and Commit, Easy tier: Review',
    })
    const next = within(callout).getByRole('button', {
      name: 'Stage and Commit, Medium tier: Continue',
    })
    const locked = within(callout).getByRole('button', {
      name: 'Stage and Commit, Hard tier: Locked',
    })

    expect(cleared).not.toHaveAttribute('data-next')
    expect(next).toHaveAttribute('data-next', 'true')
    expect(locked).toBeDisabled()
    expect(within(locked).getByText('2 waves')).toBeInTheDocument()
  })

  it('docks the callout clear of the path instead of over the nodes', () => {
    const { container } = openCallout()

    const callout = container.querySelector<HTMLElement>('.story-level-callout')
    expect(callout).not.toBeNull()
    expect(callout).toHaveAttribute('data-placement', 'docked')

    // The callout's left edge starts past every node's outer edge, so it can
    // never sit on top of one whatever the selected node's own position is.
    const left = Number.parseFloat(callout!.style.getPropertyValue('--callout-left'))
    const nodes = Array.from(container.querySelectorAll<HTMLElement>('.story-path-node'))
    expect(nodes.length).toBeGreaterThan(0)
    for (const node of nodes) {
      const nodeX = Number.parseFloat(node.style.getPropertyValue('--node-x'))
      expect(left).toBeGreaterThan(nodeX)
    }
  })

  it('closes the callout with Escape and restores focus to its node', async () => {
    const { node } = openCallout()
    expect(screen.getByRole('region', { name: 'Stage and Commit' })).toBeInTheDocument()

    fireEvent.keyDown(window, { key: 'Escape' })

    expect(screen.queryByRole('region', { name: 'Stage and Commit' })).not.toBeInTheDocument()
    await waitFor(() => expect(node).toHaveFocus())
  })

  it('closes the callout from its close button', () => {
    openCallout()

    fireEvent.click(screen.getByRole('button', { name: 'Close Stage and Commit details' }))
    expect(screen.queryByRole('region', { name: 'Stage and Commit' })).not.toBeInTheDocument()
  })
})
