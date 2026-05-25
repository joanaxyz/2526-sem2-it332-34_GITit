import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { ScenarioContextPanel } from './ScenarioContextPanel'
import type { ScenarioSession } from '@/features/practice/types'

const repositoryState = {
  commits: [],
  branches: { main: null },
  head: { type: 'branch' as const, name: 'main', target: null },
  staging: {},
  working_tree: {},
  conflicts: [],
}

const session: ScenarioSession = {
  id: 42,
  mode: 'primary',
  status: 'started',
  difficulty_instance_id: 7,
  completed_at: null,
  first_attempt_star_eligible: true,
  completion_type: 'state_based',
  scenario: {
    id: 5,
    slug: 'clean-commit',
    title: 'Commit the clean changes',
    focus: 'git commit',
    narrative: 'Legacy internal summary only.',
  },
  student_context: {
    story: 'Prepare one clean snapshot for the release notes.',
    current_state: ['You are on the main branch.'],
    required_details: [{ label: 'Target file', value: 'release-notes.md' }],
    constraints: ['Do not include scratch.md in the final snapshot.'],
  },
  module: {
    id: 3,
    number: 1,
    title: 'Basics',
  },
  difficulty: 'easy',
  variant: {
    id: 9,
    label: 'Variant A',
    changed_variant: false,
  },
  mastery_progress: {
    mastered: 0,
    required: 3,
  },
  policy: {
    id: 11,
    min_counted_commands: 3,
    max_counted_commands: 6,
    non_counted_patterns: ['git status', 'git diff'],
  },
  counts: {
    counted_action_total: 1,
    minimum_counted_commands: 3,
    maximum_counted_commands: 6,
    non_counted_diagnostic_total: 2,
    remaining_counted_commands: 5,
    max_reached: false,
    total_attempts: 3,
  },
  scaffolding: {
    live_dag: true,
    expected_state: true,
    contextual_feedback: true,
  },
  repository_state: repositoryState,
  expected_state: repositoryState,
  steps: [],
  review_mode: false,
  next_difficulty: null,
  completion: null,
}

describe('ScenarioContextPanel', () => {
  afterEach(() => cleanup())

  it('renders structured context without task or success checklist sections', () => {
    render(<ScenarioContextPanel session={session} />)

    expect(screen.getByText('Scenario Brief')).toBeInTheDocument()
    expect(screen.getByText('Repository Brief')).toBeInTheDocument()
    expect(screen.getByText('Required Details')).toBeInTheDocument()
    expect(screen.getByText('Constraints')).toBeInTheDocument()
    expect(screen.queryByText(/^Task$/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/success conditions/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/checklist/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Legacy internal summary only.')).not.toBeInTheDocument()
  })
})
