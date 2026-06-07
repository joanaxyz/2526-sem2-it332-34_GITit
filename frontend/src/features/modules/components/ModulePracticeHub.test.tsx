import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { ModulePracticeHub } from './ModulePracticeHub'

const mocks = vi.hoisted(() => ({
  moduleContent: vi.fn(),
  startSession: vi.fn(),
  startReviewSession: vi.fn(),
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
      section: createMotion('section'),
    },
    useInView: () => true,
  }
})

vi.mock('@/features/scenarios/api/scenariosApi', () => ({
  scenariosApi: {
    moduleContent: mocks.moduleContent,
    startSession: mocks.startSession,
  },
  startPayloadForPractice: (practiceKind: string, id: number) => (
    practiceKind === 'command_drill'
      ? { problem_type: 'command_drill', command_drill_id: id, source_entry_point: 'module_page' }
      : { problem_type: 'workflow_scenario', workflow_level_id: id, source_entry_point: 'module_page' }
  ),
}))

vi.mock('@/features/review/api/reviewApi', () => ({
  reviewApi: {
    startReviewSession: mocks.startReviewSession,
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
        <ModulePracticeHub
          module={{
            id: 2,
            slug: 'tracking-changes-snapshots',
            number: 2,
            title: 'Tracking Changes and Creating Snapshots',
            description: 'Stage changes and create commits.',
            sort_order: 2,
            command_topic_count: 2,
            workflow_scenario_count: 1,
            practice_completion: { value: 0, numerator: 0, denominator: 5 },
          }}
        />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ModulePracticeHub', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('shows one command adventure action instead of dumping every command level', async () => {
    mocks.moduleContent.mockImplementation((_moduleId: number, section: string) => {
      if (section === 'command_adventures') {
        return Promise.resolve({
          section,
          next_cursor: null,
          results: [
            {
              item_type: 'command_drill_adventure',
              id: 2,
              slug: 'tracking-command-drill-adventure',
              title: 'Preparing File Changes',
              description: 'Learn how to inspect, stage, and save file changes.',
              practice_kind: 'command_drill',
              progress: { value: 0, numerator: 0, denominator: 5, levels_completed: 0, level_count: 2 },
              levels: [
                {
                  id: 20,
                  slug: 'git-add',
                  number: 1,
                  label: 'Level 1',
                  status: 'not_started',
                  unlocked: true,
                  usage_count: 1,
                  drill_count: 1,
                  variant_count: 1,
                  progress: { value: 0, numerator: 0, denominator: 3 },
                  next_practice: {
                    id: 101,
                    practice_kind: 'command_drill',
                    slug: 'stage-one-file',
                    title: 'Stage one file',
                    summary: 'Stage a requested path.',
                    status: 'not_started',
                    required_successful_attempts: 3,
                    successful_attempts: { count: 0, required: 3 },
                    active_session_id: null,
                    latest_attempt: null,
                    completion: null,
                    review_available: false,
                    command_budget: { min_counted_commands: 1, max_counted_commands: 3 },
                  },
                },
                {
                  id: 21,
                  slug: 'git-commit',
                  number: 2,
                  label: 'Level 2',
                  status: 'locked',
                  unlocked: false,
                  usage_count: 1,
                  drill_count: 1,
                  variant_count: 1,
                  progress: { value: 0, numerator: 0, denominator: 2 },
                  next_practice: null,
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
            item_type: 'workflow_scenario',
            id: 30,
            slug: 'stage-commit-switch',
            title: 'Stage, Commit, Then Switch Branches',
            summary: 'Combine staging, committing, and branch switching.',
            narrative: '',
            command_topics: ['git add', 'git commit', 'git switch'],
            levels: ['easy', 'medium', 'hard'].map((difficulty, index) => ({
              id: 300 + index,
              difficulty,
              practice_kind: 'workflow_scenario',
              status: difficulty === 'easy' ? 'not_started' : 'locked',
              required_successful_attempts: 2,
              successful_attempts: { count: 0, required: 2 },
              active_session_id: null,
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

    await waitFor(() => expect(screen.getByText('Preparing File Changes')).toBeInTheDocument())
    const adventureSection = screen.getByText('Command Adventure').closest('section')
    expect(adventureSection).not.toBeNull()

    const adventure = within(adventureSection as HTMLElement)
    expect(adventure.getByText('0/5')).toBeInTheDocument()
    expect(adventure.getByRole('button', { name: /start/i })).toBeInTheDocument()
    expect(adventure.queryByText('Level 1')).not.toBeInTheDocument()
    expect(adventure.queryByText('Level 2')).not.toBeInTheDocument()
    expect(adventure.queryByText(/git add/i)).not.toBeInTheDocument()
    expect(adventure.queryByText(/easy/i)).not.toBeInTheDocument()
    expect(adventure.queryByText(/medium/i)).not.toBeInTheDocument()
    expect(adventure.queryByText(/hard/i)).not.toBeInTheDocument()

    expect(screen.getByText('Stage, Commit, Then Switch Branches')).toBeInTheDocument()
    expect(screen.getAllByText(/easy/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/medium/i).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/hard/i).length).toBeGreaterThan(0)
  })
})
