import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { DoorOverview } from './DoorOverview'
import { StoreyPracticeHub } from './StoreyPracticeHub'
import { TowerActionButton } from './TowerActionButton'
import { useTowerSelection } from '@/features/storeys/hooks/useTowerSelection'

const mocks = vi.hoisted(() => ({
  storeyContent: vi.fn(),
  startChallengeRun: vi.fn(),
  retryChallengeRun: vi.fn(),
}))

vi.mock('motion/react', async () => {
  const React = await import('react')
  const createMotion = (tag: keyof HTMLElementTagNameMap) => {
    const Component = ({ children, ...props }: Record<string, unknown> & { children?: React.ReactNode }) => {
      const domProps = { ...props }
      delete domProps.initial
      delete domProps.whileInView
      delete domProps.viewport
      delete domProps.transition
      delete domProps.variants
      return React.createElement(tag, domProps, children)
    }
    return Component
  }
  return {
    motion: {
      article: createMotion('article'),
      aside: createMotion('aside'),
      button: createMotion('button'),
      div: createMotion('div'),
      header: createMotion('header'),
      section: createMotion('section'),
      span: createMotion('span'),
    },
    useInView: () => true,
  }
})

vi.mock('@/features/challenges/api/challengesApi', () => ({
  challengesApi: {
    storeyContent: mocks.storeyContent,
    startChallengeRun: mocks.startChallengeRun,
    retryChallengeRun: mocks.retryChallengeRun,
  },
}))

function mockCanonicalStoreyContent() {
  mocks.storeyContent.mockImplementation((_storeyId: number, section: string) => {
    if (section === 'command_adventures') {
      return Promise.resolve({
        section,
        next_cursor: null,
        results: [
          {
            item_type: 'command_adventure',
            id: 2,
            slug: 'tracking-command-adventure',
            title: 'Preparing File Changes',
            description: 'Learn how to inspect, stage, and save file changes.',
            status: 'not_started',
            is_passed: false,
            active_run_id: null,
            latest_run_id: null,
            quest_count: 5,
            progress: { value: 0, numerator: 0, denominator: 5 },
          },
        ],
      })
    }
    if (section === 'tomes') {
      return Promise.resolve({
        section,
        next_cursor: null,
        results: [
          {
            item_type: 'tome',
            id: 7,
            slug: 'how-git-thinks',
            title: 'How Git Thinks',
            summary: 'The four places your work lives.',
            placement: 'above_adventure',
            pages: [
              {
                id: 'overview',
                title: 'The four places',
                heading: 'The four places',
                section_type: 'overview',
                blocks: [{ type: 'paragraph', body: 'Every Git command moves work between four places.' }],
              },
            ],
          },
        ],
      })
    }
    return Promise.resolve({
      section,
      next_cursor: null,
      results: [
        {
          item_type: 'challenge',
          id: 30,
          slug: 'stage-commit-switch',
          title: 'Stage, Commit, Then Switch Branches',
          summary: 'Combine staging, committing, and branch switching.',
          narrative: '',
          quests: ['easy', 'medium', 'hard'].map((difficulty, index) => ({
            id: 300 + index,
            difficulty,
            status: difficulty === 'easy' ? 'not_started' : 'locked',
            required_successful_attempts: 2,
            successful_attempts: { count: 0, required: 2 },
            active_run_id: null,
            latest_attempt: null,
            completion: null,
            review_available: false,
            command_budget: { min_counted_commands: 3, max_counted_commands: 6 },
          })),
        },
      ],
    })
  })
}

function renderHub() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <StoreyPracticeHub
          storey={{
            id: 2,
            slug: 'tracking-changes-snapshots',
            number: 2,
            title: 'Tracking Changes and Creating Snapshots',
            description: 'Stage changes and create commits.',
            sort_order: 2,
            command_skill_count: 2,
            challenge_count: 1,
            practice_completion: { value: 0, numerator: 0, denominator: 5 },
          }}
        />
        <DoorOverview storeyId={2} />
        <TowerActionButton />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('StoreyPracticeHub', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
    useTowerSelection.setState({ selected: null })
  })

  it('renders a balcony adventure door and one door per challenge quest', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    await waitFor(() =>
      expect(
        screen.getByRole('button', { name: /select command adventure: preparing file changes/i }),
      ).toBeInTheDocument(),
    )
    expect(
      screen.getByRole('button', { name: /select stage, commit, then switch branches: easy/i }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /select stage, commit, then switch branches: medium/i }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /select stage, commit, then switch branches: hard/i }),
    ).toBeInTheDocument()
  })

  it('shows the adventure overview + Play action when its door is selected', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const door = await screen.findByRole('button', { name: /select command adventure: preparing file changes/i })
    fireEvent.click(door)

    const overview = screen.getByLabelText('Selected stage')
    expect(within(overview).getByText('Preparing File Changes')).toBeInTheDocument()
    expect(within(overview).getByText('0/5 solved')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^play$/i })).toBeInTheDocument()
  })

  it('renders the tome lectern above the adventure and opens the reader via Read', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const lectern = await screen.findByRole('button', { name: /select tome: how git thinks/i })
    const adventureDoor = await screen.findByRole('button', {
      name: /select command adventure: preparing file changes/i,
    })
    // The tome section is authored above the adventure gate.
    expect(lectern.compareDocumentPosition(adventureDoor) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    fireEvent.click(lectern)

    const overview = screen.getByLabelText('Selected stage')
    expect(within(overview).getByText('Tome')).toBeInTheDocument()
    expect(within(overview).getByText('How Git Thinks')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /^read$/i }))
    await waitFor(() => expect(screen.getByText('The four places')).toBeInTheDocument())
  })

  it('does not render a tome section when the storey has no authored tome', async () => {
    mocks.storeyContent.mockImplementation((_storeyId: number, section: string) => {
      if (section === 'tomes') return Promise.resolve({ section, next_cursor: null, results: [] })
      return Promise.resolve({ section, next_cursor: null, results: [] })
    })
    renderHub()

    await waitFor(() => expect(mocks.storeyContent).toHaveBeenCalled())
    expect(screen.queryByRole('button', { name: /select tome/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: /^tome$/i })).not.toBeInTheDocument()
  })

  it('shows the chosen quest overview with accuracy + attempts when a trial door is selected', async () => {
    mockCanonicalStoreyContent()
    renderHub()

    const easyDoor = await screen.findByRole('button', {
      name: /select stage, commit, then switch branches: easy/i,
    })
    fireEvent.click(easyDoor)

    const overview = screen.getByLabelText('Selected stage')
    expect(within(overview).getByText('Stage, Commit, Then Switch Branches')).toBeInTheDocument()
    expect(within(overview).getByText('Easy')).toBeInTheDocument()
    // Accuracy with no attempts yet renders as a placeholder.
    expect(within(overview).getByText('--%')).toBeInTheDocument()
  })
})
