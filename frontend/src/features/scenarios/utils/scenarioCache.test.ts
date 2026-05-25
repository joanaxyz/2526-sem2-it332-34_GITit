import { describe, expect, it } from 'vitest'

import type { ScenarioSession } from '@/features/practice/types'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import { updateScenarioListWithSession, updateScenarioSummaryWithSession } from './scenarioCache'

const scenario: ScenarioSkillFocus = {
  id: 10,
  slug: 'branch-rescue',
  title: 'Branch rescue',
  focus: 'Branching',
  summary: 'Move work safely.',
  short_explanation: 'Learn how branch pointers and HEAD relate.',
  skill_focus_type: 'concept_specific',
  primary_focus_commands: ['git branch', 'git switch'],
  supporting_diagnostic_commands: ['git status'],
  safe_demo_commands: ['git branch'],
  demo_repository_state: {
    commits: [],
    branches: {},
    head: { type: 'branch', name: 'main', target: null },
    staging: {},
    working_tree: {},
    conflicts: [],
  },
  demo_dag_config: {},
  demo_explanation_steps: [],
  related_git_concepts: ['HEAD'],
  learning_unit_id: 2,
  lesson_id: 5,
  difficulties: [
    {
      id: 101,
      difficulty: 'easy',
      status: 'in_progress',
      review_available: false,
      mastery_progress: { mastered: 0, required: 3 },
      active_session_id: 900,
      retry_session_id: null,
      policy: { id: 1, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
      completion: null,
      latest_attempt: {
        id: 900,
        status: 'started',
        accuracy_rate: null,
        command_accurate: null,
        counted_action_total: 0,
        total_attempts: 0,
        completed_at: null,
        ended_at: null,
      },
    },
    {
      id: 102,
      difficulty: 'medium',
      status: 'locked',
      review_available: false,
      mastery_progress: { mastered: 0, required: 3 },
      active_session_id: null,
      retry_session_id: null,
      policy: { id: 2, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
      completion: null,
      latest_attempt: null,
    },
    {
      id: 103,
      difficulty: 'hard',
      status: 'locked',
      review_available: false,
      mastery_progress: { mastered: 0, required: 3 },
      active_session_id: null,
      retry_session_id: null,
      policy: { id: 3, min_counted_commands: 1, max_counted_commands: 5, non_counted_patterns: [] },
      completion: null,
      latest_attempt: null,
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
  completion_type: 'state_based',
  scenario: {
    id: 10,
    slug: 'branch-rescue',
    title: 'Branch rescue',
    focus: 'Branching',
    narrative: 'Move work safely.',
  },
  module: {
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
  mastery_progress: { mastered: 3, required: 3 },
  mastered_records: { mastered: 3, required: 3 },
  completion: {
    first_attempt_star: true,
    counted_action_total: 2,
    completed_at: '2026-05-18T12:00:00Z',
  },
  policy: { id: 1, min_counted_commands: 2, max_counted_commands: 6, non_counted_patterns: [] },
  counts: {
    counted_action_total: 2,
    minimum_counted_commands: 2,
    maximum_counted_commands: 6,
    non_counted_diagnostic_total: 1,
    remaining_counted_commands: 4,
    max_reached: false,
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
  next_difficulty: {
    id: 102,
    difficulty: 'medium',
  },
}

describe('updateScenarioListWithSession', () => {
  it('patches only the completed scenario difficulty and unlocks the next difficulty', () => {
    const [updated] = updateScenarioListWithSession([scenario], completedSession) ?? []

    expect(updated.difficulties[0]).toMatchObject({
      status: 'completed',
      review_available: true,
      retry_session_id: null,
      active_session_id: null,
      completion: {
        first_attempt_star: true,
        counted_action_total: 2,
        completed_at: '2026-05-18T12:00:00Z',
      },
      latest_attempt: {
        id: 900,
        status: 'completed',
        accuracy_rate: 100,
        command_accurate: true,
        counted_action_total: 2,
      },
    })
    expect(updated.difficulties[1].status).toBe('not_started')
    expect(updated.difficulties[2].status).toBe('locked')
  })

  it('unlocks the next backend-provided difficulty without assuming only three levels', () => {
    const scenarioWithExtraHard: ScenarioSkillFocus = {
      ...scenario,
      difficulties: [
        ...scenario.difficulties,
        {
          ...scenario.difficulties[2],
          id: 104,
          difficulty: 'extra hard',
          status: 'locked',
        },
      ],
    }
    const completedHardSession: ScenarioSession = {
      ...completedSession,
      difficulty_instance_id: 103,
      difficulty: 'hard',
      next_difficulty: {
        id: 104,
        difficulty: 'extra hard',
      },
    }

    const [updated] = updateScenarioListWithSession([scenarioWithExtraHard], completedHardSession) ?? []

    expect(updated.difficulties[2].status).toBe('completed')
    expect(updated.difficulties[3]).toMatchObject({
      difficulty: 'extra hard',
      status: 'not_started',
    })
  })

  it('keeps unrelated scenario lists by reference', () => {
    const unrelated = [{ ...scenario, id: 99 }]

    expect(updateScenarioListWithSession(unrelated, completedSession)).toBe(unrelated)
  })

  it('patches module scenario summaries that seed expanded module cards', () => {
    const summary = {
      '2': [scenario],
      '3': [{ ...scenario, id: 99 }],
    }

    const updated = updateScenarioSummaryWithSession(summary, completedSession)

    expect(updated?.['2'][0].difficulties[0]).toMatchObject({
      status: 'completed',
      review_available: true,
      latest_attempt: {
        accuracy_rate: 100,
      },
    })
    expect(updated?.['3']).toBe(summary['3'])
  })

  it('calculates command accuracy from target actions versus used actions', () => {
    const sessionWithExtraAction: ScenarioSession = {
      ...completedSession,
      mastery_progress: { mastered: 2, required: 3 },
      counts: {
        ...completedSession.counts,
        counted_action_total: 3,
      },
    }
    const [updated] = updateScenarioListWithSession([scenario], sessionWithExtraAction) ?? []

    expect(updated.difficulties[0].latest_attempt?.accuracy_rate).toBe(67)
    expect(updated.difficulties[0].latest_attempt?.command_accurate).toBe(false)
    expect(updated.difficulties[0].review_available).toBe(false)
    expect(updated.difficulties[0].retry_session_id).toBe(sessionWithExtraAction.id)
  })

  it('uses the latest retry attempt for mastery and retry routing', () => {
    const completedDifficulty = {
      ...scenario.difficulties[0],
      status: 'completed' as const,
      active_session_id: null,
      retry_session_id: 900,
      completion: {
        first_attempt_star: false,
        counted_action_total: 3,
        completed_at: '2026-05-18T12:00:00Z',
      },
      latest_attempt: {
        id: 900,
        status: 'completed' as const,
        accuracy_rate: 67,
        command_accurate: false,
        counted_action_total: 3,
        total_attempts: 4,
        completed_at: '2026-05-18T12:00:00Z',
        ended_at: '2026-05-18T12:00:00Z',
      },
    }
    const completedScenario = {
      ...scenario,
      difficulties: [completedDifficulty, ...scenario.difficulties.slice(1)],
    }
    const activeRetry: ScenarioSession = {
      ...completedSession,
      id: 901,
      status: 'started',
      completed_at: null,
      mastery_progress: { mastered: 1, required: 3 },
      counts: {
        ...completedSession.counts,
        counted_action_total: 0,
        total_attempts: 0,
      },
    }
    const [activeUpdated] = updateScenarioListWithSession([completedScenario], activeRetry) ?? []

    expect(activeUpdated.difficulties[0]).toMatchObject({
      status: 'completed',
      active_session_id: 901,
      retry_session_id: null,
      latest_attempt: {
        id: 901,
        accuracy_rate: null,
      },
    })

    const abandonedRetry: ScenarioSession = {
      ...activeRetry,
      status: 'abandoned',
    }
    const [abandonedUpdated] = updateScenarioListWithSession([completedScenario], abandonedRetry) ?? []

    expect(abandonedUpdated.difficulties[0]).toMatchObject({
      status: 'completed',
      active_session_id: null,
      retry_session_id: 901,
      latest_attempt: {
        id: 901,
        accuracy_rate: 0,
      },
    })
  })
})
