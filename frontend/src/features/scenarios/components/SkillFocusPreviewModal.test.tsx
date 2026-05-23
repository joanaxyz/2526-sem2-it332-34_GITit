import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { SkillFocusPreviewModal } from './SkillFocusPreviewModal'
import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type { DifficultyAccess, ScenarioSkillFocus } from '@/features/scenarios/types'

vi.mock('@/features/scenarios/api/scenariosApi', () => ({
  scenariosApi: {
    getSkillFocus: vi.fn(),
    submitDemoCommand: vi.fn(),
  },
}))

const snapshot = {
  commits: [],
  branches: { main: null },
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: { 'demo.txt': 'modified' },
  conflicts: [],
}

const scenario: ScenarioSkillFocus = {
  id: 1,
  slug: 'inspect-repository-state',
  title: 'Inspect repository state before acting',
  focus: 'diagnostic commands',
  summary: 'Practice read-only commands.',
  short_explanation: 'Read the repository before acting.',
  skill_focus_type: 'concept_specific',
  primary_focus_commands: ['git status', 'git log --oneline'],
  supporting_inspection_commands: ['git diff', 'git diff --staged'],
  safe_demo_commands: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
  demo_repository_state: snapshot,
  demo_explanation_steps: [],
  command_preview: {
    title: 'Command preview',
    command_title: 'Inspect repository state before acting',
    syntax_examples: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
    supported_demo_commands: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
    demo_steps: [],
    before_state: snapshot,
    after_state: snapshot,
    short_explanation: 'Read before acting.',
    common_mistakes: ['Skipping inspection before acting.'],
    diagnostic: true,
    counted: false,
  },
  related_git_concepts: [],
  learning_unit_id: 1,
  module_id: 1,
  lesson_id: 1,
  difficulties: [],
}

const difficulty: DifficultyAccess = {
  id: 10,
  difficulty: 'easy',
  status: 'not_started',
  review_available: false,
  mastery_progress: { mastered: 0, required: 1 },
  active_session_id: null,
  retry_session_id: null,
  policy: { id: 1, min_counted_commands: 0, max_counted_commands: 0 },
  completion: null,
  latest_attempt: null,
}

function renderPreview() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  vi.mocked(scenariosApi.getSkillFocus).mockResolvedValue(scenario)
  vi.mocked(scenariosApi.submitDemoCommand).mockResolvedValue({
    repository_state: snapshot,
    terminal_output: 'On branch main',
    was_processable: true,
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <SkillFocusPreviewModal
        scenario={scenario}
        difficulty={difficulty}
        action="start"
        isProceeding={false}
        onClose={vi.fn()}
        onProceed={vi.fn()}
      />
    </QueryClientProvider>,
  )
}

describe('SkillFocusPreviewModal', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('renders as Command preview with persistent previous and next controls', async () => {
    renderPreview()

    expect((await screen.findAllByText('Command preview')).length).toBeGreaterThan(0)
    await screen.findByText('Inspect repository state before acting')
    expect(screen.getByRole('button', { name: /previous/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /next/i })).not.toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: /next/i }))

    expect(screen.getByRole('button', { name: /previous/i })).not.toBeDisabled()
  })

  it('submits every command listed in preview metadata', async () => {
    renderPreview()
    await screen.findAllByText('Command preview')
    await screen.findByText('Inspect repository state before acting')

    for (const command of scenario.command_preview!.supported_demo_commands) {
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: command } })
      fireEvent.click(screen.getByRole('button', { name: 'Run' }))
      await waitFor(() => expect(scenariosApi.submitDemoCommand).toHaveBeenCalledWith(scenario.slug, expect.objectContaining({ command })))
    }
  })
})
