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

const demoSteps = [
  {
    command: 'git status',
    title: 'Check status',
    explanation: 'Check the branch and dirty paths before deciding what to do next.',
    repository_state: snapshot,
    common_mistake: 'Do not treat status as a fix; it only reports state.',
    diagnostic: true,
    counted: false,
  },
  {
    command: 'git diff',
    title: 'Inspect unstaged changes',
    explanation: 'Read the unstaged file changes before staging anything.',
    repository_state: snapshot,
    common_mistake: 'Do not use git diff --staged when nothing is staged yet.',
    diagnostic: true,
    counted: false,
  },
]

const scenario: ScenarioSkillFocus = {
  id: 1,
  slug: 'inspect-repository-state',
  title: 'Inspect repository state before acting',
  focus: 'diagnostic commands',
  summary: 'Practice read-only commands.',
  short_explanation: 'Read the repository before acting.',
  skill_focus_type: 'concept_specific',
  primary_focus_commands: ['git status', 'git log --oneline'],
  supporting_diagnostic_commands: ['git diff', 'git diff --staged'],
  safe_demo_commands: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
  demo_repository_state: snapshot,
  demo_explanation_steps: demoSteps,
  command_preview: {
    schema_version: 2,
    title: 'Command preview',
    intro: 'Read before acting.',
    purpose: 'Learn what these diagnostic commands report before starting.',
    focus_label: 'diagnostic commands',
    command_title: 'Inspect repository state before acting',
    commands: [
      {
        id: 'git-status',
        key: 'git-status',
        base_command: 'git status',
        title: 'git status',
        command: 'git status',
        canonical_command: 'git status',
        summary: 'Check the branch and dirty paths before deciding what to do next.',
        pages: [
          {
            id: 'overview',
            title: 'Introduction',
            heading: 'What git status is for',
            eyebrow: 'git status',
            section_type: 'overview',
            blocks: [
              { type: 'paragraph', body: 'git status is the first read-only diagnostic command.' },
              { type: 'terminal_output', title: 'Typical output', body: 'On branch main' },
            ],
          },
          {
            id: 'status-syntax',
            title: 'Details',
            heading: 'Status behavior',
            eyebrow: 'git status',
            section_type: 'syntax',
            blocks: [
              { type: 'command', title: 'Command syntax', items: ['git status'] },
              { type: 'warning', title: 'Common mistake', body: 'Do not treat status as a fix; it only reports state.' },
            ],
          },
          {
            id: 'option-short',
            title: 'Option: -s',
            heading: 'Short status',
            eyebrow: '-s',
            section_type: 'option',
            blocks: [
              { type: 'paragraph', body: 'Use -s when the scenario wants compact status output.' },
            ],
          },
        ],
        demo_steps: [demoSteps[0]],
      },
      {
        id: 'git-diff',
        key: 'git-diff',
        base_command: 'git diff',
        title: 'git diff',
        command: 'git diff',
        canonical_command: 'git diff',
        summary: 'Read the unstaged file changes before staging anything.',
        pages: [
          {
            id: 'diff-overview',
            title: 'Overview',
            eyebrow: 'git diff',
            section_type: 'overview',
            blocks: [
              { type: 'paragraph', body: 'Read the unstaged file changes before staging anything.' },
              { type: 'bullet_list', title: 'Boundaries', items: ['It does not show staged changes unless you use --staged.'] },
            ],
          },
        ],
        demo_steps: [demoSteps[1]],
      },
    ],
    syntax_examples: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
    supported_demo_commands: ['git status', 'git log --oneline', 'git diff', 'git diff --staged'],
    demo_steps: demoSteps,
    before_state: snapshot,
    after_state: snapshot,
    short_explanation: 'Read before acting.',
    common_mistakes: ['Skipping diagnostics before acting.'],
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

function pagedScenario(commandIndex: number): ScenarioSkillFocus {
  const preview = scenario.command_preview!
  const commands = preview.commands!.map((command, index) => (
    index === commandIndex
      ? command
      : {
          ...command,
          sections: [],
          pages: [],
          demo_steps: [],
          page_count: command.pages.length,
          demo_step_count: command.demo_steps?.length ?? 0,
        }
  ))
  return {
    ...scenario,
    command_preview: {
      ...preview,
      commands,
      navigation: {
        current_index: commandIndex,
        total_count: commands.length,
        commands: commands.map((command) => ({
          ...command,
          sections: [],
          pages: [],
          demo_steps: [],
        })),
      },
    },
  }
}

describe('SkillFocusPreviewModal', () => {
  afterEach(() => {
    cleanup()
    vi.clearAllMocks()
  })

  it('renders one continuous command lesson with one shared demo area', async () => {
    renderPreview()

    expect(await screen.findByText('What git status is for')).toBeInTheDocument()
    expect(screen.getByText('Status behavior')).toBeInTheDocument()
    expect(screen.getByText('Short status')).toBeInTheDocument()
    expect(screen.queryByText('Diagnostic command preview')).not.toBeInTheDocument()
    expect(screen.queryByText('Command preview')).not.toBeInTheDocument()
    expect(screen.getByText('git status is the first read-only diagnostic command.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /start scenario/i })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /next page/i })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /previous page/i })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /previous command/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /next command/i })).not.toBeDisabled()
    expect(screen.getByRole('button', { name: /open contents/i })).toBeInTheDocument()
    expect(screen.getAllByText('git status').length).toBeGreaterThan(0)
  })

  it('uses the compact footer navigator for commands', async () => {
    renderPreview()
    await screen.findByText('What git status is for')

    fireEvent.click(screen.getByRole('button', { name: /next command/i }))
    expect(screen.getByText('Read the unstaged file changes before staging anything.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /previous command/i })).not.toBeDisabled()

    fireEvent.click(screen.getByRole('button', { name: /open demo/i }))
    expect(screen.getByText('Try it')).toBeInTheDocument()
    expect(screen.getByText('Inline command demo')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /back to command guide/i })).toBeInTheDocument()
  })

  it('requests the selected command page from the backend paginator', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    vi.mocked(scenariosApi.getSkillFocus).mockImplementation((_slug, options) =>
      Promise.resolve(pagedScenario(options?.commandIndex ?? 0)),
    )

    render(
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

    await screen.findByText('What git status is for')
    expect(screen.queryByText('Read the unstaged file changes before staging anything.')).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /next command/i }))

    await waitFor(() => expect(scenariosApi.getSkillFocus).toHaveBeenCalledWith(scenario.slug, { commandIndex: 1 }))
    expect(await screen.findByText('Read the unstaged file changes before staging anything.')).toBeInTheDocument()
  })

  it('switches commands while preserving terminal history', async () => {
    renderPreview()
    await screen.findByText('What git status is for')
    fireEvent.click(screen.getByRole('button', { name: /open demo/i }))

    const input = screen.getByRole('textbox')
    fireEvent.change(input, { target: { value: 'git status' } })
    fireEvent.click(screen.getByRole('button', { name: 'Run' }))

    await screen.findByText('On branch main')
    fireEvent.click(screen.getByRole('button', { name: /open contents/i }))
    expect(screen.getByRole('dialog', { name: /command contents/i })).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /open git diff/i }))

    expect(screen.getByText('Read the unstaged file changes before staging anything.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: /open demo/i }))
    expect(screen.getByText('On branch main')).toBeInTheDocument()
  })

  it('uses command and option anchors in the contents panel', async () => {
    renderPreview()
    await screen.findByText('What git status is for')

    fireEvent.click(screen.getByRole('button', { name: /open contents/i }))
    expect(screen.getByText('Commands')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Open git status' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Jump to git status -s' })).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Jump to git status -s' }))
    expect(screen.queryByRole('dialog', { name: /command contents/i })).not.toBeInTheDocument()
    expect(screen.getByText('Use -s when the scenario wants compact status output.')).toBeInTheDocument()
  })

  it('submits every command listed in preview metadata', async () => {
    renderPreview()
    await screen.findByText('What git status is for')
    fireEvent.click(screen.getByRole('button', { name: /open demo/i }))

    for (const command of scenario.command_preview!.supported_demo_commands) {
      const input = screen.getByRole('textbox')
      fireEvent.change(input, { target: { value: command } })
      fireEvent.click(screen.getByRole('button', { name: 'Run' }))
      await waitFor(() => expect(scenariosApi.submitDemoCommand).toHaveBeenCalledWith(scenario.slug, expect.objectContaining({ command })))
    }
  })
})
