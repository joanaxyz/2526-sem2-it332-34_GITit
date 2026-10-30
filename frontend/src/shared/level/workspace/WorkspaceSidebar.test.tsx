import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { WorkspaceRun } from '@/shared/level/workspace/types'

vi.mock('@/shared/level/components/ProjectStructurePanel', () => ({
  ProjectStructurePanel: () => <div data-testid="project-structure">Project files</div>,
}))

vi.mock('@/shared/level/workspace/ContextualFeedbackPanel', () => ({
  ContextualFeedbackPanel: () => <div data-testid="feedback-panel">Contextual Feedback</div>,
}))

import { WorkspaceSidebar } from './WorkspaceSidebar'

function makeRun(contextualFeedback: boolean): WorkspaceRun {
  return {
    id: 7,
    status: 'started',
    scenario_context: { schema_version: 3, story: 'Story', task: 'Initialize the repository.' },
    variant: { id: 1, label: 'Initialize the current folder', changed_variant: false },
    scaffolding: { live_dag: true, expected_state: false, contextual_feedback: contextualFeedback },
    repository_state: {},
  } as unknown as WorkspaceRun
}

function renderSidebar(run: WorkspaceRun, { teachingActive = false, projectFilesOpen = true } = {}) {
  render(
    <WorkspaceSidebar
      run={run}
      scene={{ rootName: 'initializing-a-local-repository', title: 'Initializing Repositories' }}
      teachingActive={teachingActive}
      projectFilesOpen={projectFilesOpen}
      workspaceEditorPath={null}
      createDisabled={false}
      onToggleProjectFiles={vi.fn()}
      onCreateFile={vi.fn()}
      onRenameFile={vi.fn()}
      onDeleteFile={vi.fn()}
      onOpenFile={vi.fn()}
    />,
  )
  return screen.getByTestId('tier-workspace-sidebar')
}

afterEach(cleanup)

describe('WorkspaceSidebar', () => {
  it('stacks Objectives, Project files and Contextual feedback when the difficulty gives feedback', () => {
    const sidebar = renderSidebar(makeRun(true))

    expect(sidebar).toHaveClass('has-feedback')
    expect(screen.getByRole('list', { name: 'Objectives' })).toHaveTextContent('Initialize the repository.')
    expect(screen.getByTestId('project-structure')).toBeInTheDocument()
    expect(screen.getByTestId('tier-feedback-region')).not.toHaveClass('is-suspended')
    expect(screen.getByTestId('feedback-panel')).toBeInTheDocument()
  })

  it('drops the feedback card entirely on a difficulty without feedback', () => {
    const sidebar = renderSidebar(makeRun(false))

    expect(sidebar).not.toHaveClass('has-feedback')
    expect(screen.queryByTestId('tier-feedback-region')).not.toBeInTheDocument()
    expect(screen.getByTestId('project-structure')).toBeInTheDocument()
  })

  it('keeps the feedback card space while a command guide teaches', () => {
    const sidebar = renderSidebar(makeRun(true), { teachingActive: true })

    expect(sidebar).toHaveClass('has-feedback')
    expect(screen.getByTestId('tier-feedback-region')).toHaveClass('is-suspended')
  })

  it('marks the column when project files are collapsed', () => {
    const sidebar = renderSidebar(makeRun(true), { projectFilesOpen: false })

    expect(sidebar).toHaveClass('is-files-collapsed')
  })
})
