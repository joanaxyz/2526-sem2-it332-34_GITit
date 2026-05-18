import { describe, expect, it } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import { updateScenarioListWithSession } from './scenarioCache'

const scenario: ScenarioSkillFocus = {
  id: 10,
  slug: 'branch-rescue',
  title: 'Branch rescue',
  focus: 'Branching',
  narrative: 'Move work safely.',
  task_prompt: 'Recover the misplaced commit.',
  learning_unit_id: 2,
  lesson_id: 5,
  difficulties: [
    {
      id: 101,
      difficulty: 'easy',
      narrative: 'Easy setup.',
      task_prompt: 'Recover the misplaced commit.',
      status: 'in_progress',
      review_available: false,
      active_session_id: 900,
      policy: { id: 1, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
      completion: null,
    },
    {
      id: 102,
      difficulty: 'medium',
      narrative: 'Medium setup.',
      task_prompt: 'Recover a busier misplaced commit.',
      status: 'locked',
      review_available: false,
      active_session_id: null,
      policy: { id: 2, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
      completion: null,
    },
    {
      id: 103,
      difficulty: 'hard',
      narrative: 'Hard setup.',
      task_prompt: 'Recover a complex misplaced commit.',
      status: 'locked',
      review_available: false,
      active_session_id: null,
      policy: { id: 3, min_counted_commands: 1, max_counted_commands: 5, non_counted_patterns: [] },
      completion: null,
    },
  ],
}

const completedSession: ScenarioSession = {
  id: 900,
  mode: 'primary',
  status: 'completed',
  difficulty_instance_id: 101,
  completed_at: '2026-05-18T12:00:00Z',
  first_attempt_star_eligible: true,
  scenario: {
    id: 10,
    slug: 'branch-rescue',
    title: 'Branch rescue',
    focus: 'Branching',
    narrative: 'Move work safely.',
    task_prompt: 'Recover the misplaced commit.',
  },
  unit: {
    id: 2,
    number: 2,
    title: 'Branches',
  },
  difficulty: 'easy',
  variant: {
    id: 77,
    label: 'A',
    changed_variant: false,
  },
  policy: { id: 1, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
  counts: {
    counted_action_total: 2,
    non_counted_diagnostic_total: 1,
    remaining_counted_commands: 4,
    total_attempts: 3,
  },
  scaffolding: {
    live_dag: true,
    expected_state: true,
    contextual_feedback: true,
  },
  repository_state: {
    commits: [],
    branches: {},
    head: { type: 'branch', name: 'main', target: null },
    staging: {},
    working_tree: {},
    conflicts: [],
  },
  expected_state: null,
  steps: [],
  review_mode: false,
}

describe('updateScenarioListWithSession', () => {
  it('patches only the completed scenario difficulty and unlocks the next difficulty', () => {
    const [updated] = updateScenarioListWithSession([scenario], completedSession) ?? []

    expect(updated.difficulties[0]).toMatchObject({
      status: 'complete',
      review_available: true,
      active_session_id: null,
      completion: {
        first_attempt_star: true,
        counted_action_total: 2,
        completed_at: '2026-05-18T12:00:00Z',
      },
    })
    expect(updated.difficulties[1].status).toBe('available')
    expect(updated.difficulties[2].status).toBe('locked')
  })

  it('keeps unrelated scenario lists by reference', () => {
    const unrelated = [{ ...scenario, id: 99 }]

    expect(updateScenarioListWithSession(unrelated, completedSession)).toBe(unrelated)
  })
})
