import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { StoreyPracticeHub } from './StoreyPracticeHub'

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
      return React.createElement(tag, domProps, children)
    }
    return Component
  }
  return {
    motion: {
      article: createMotion('article'),
      aside: createMotion('aside'),
      div: createMotion('div'),
      header: createMotion('header'),
      section: createMotion('section'),
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
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('StoreyPracticeHub', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('renders command adventure and challenge content from canonical storey payloads', async () => {
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
              active_run_id: null,
              latest_run_id: null,
              problem_count: 5,
              progress: { value: 0, numerator: 0, denominator: 5 },
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
            command_topics: ['git add', 'git commit', 'git switch'],
            levels: ['easy', 'medium', 'hard'].map((difficulty, index) => ({
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

    renderHub()

    await waitFor(() => expect(screen.getByText('0/5')).toBeInTheDocument())
    const adventureSection = screen.getByText('Command Adventure').closest('section')
    expect(adventureSection).not.toBeNull()

    const adventure = within(adventureSection as HTMLElement)
    expect(adventure.getByText('0/5')).toBeInTheDocument()
    expect(adventure.getByRole('button', { name: /start/i })).toBeInTheDocument()

    expect(screen.getByText('Stage, Commit, Then Switch Branches')).toBeInTheDocument()
    expect(screen.getAllByText(/easy/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/medium/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/hard/i).length).toBeGreaterThan(0)
  })
})
