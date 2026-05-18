import type { Difficulty } from '@/features/scenarios/types'

export type RepositoryCommit = {
  id: string
  message: string
  parents: string[]
}

export type RepositorySnapshot = {
  commits: RepositoryCommit[]
  branches: Record<string, string | null>
  head: {
    type: 'branch' | 'detached'
    name?: string
    target?: string | null
  }
  staging: Record<string, string>
  working_tree: Record<string, string>
  conflicts: string[]
}

export type ScenarioSession = {
  id: number
  mode: 'primary' | 'review'
  status: 'started' | 'completed' | 'failed' | 'abandoned'
  scenario: {
    id: number
    slug: string
    title: string
    focus: string
    narrative: string
    task_prompt: string
  }
  unit: {
    id: number
    number: number
    title: string
  }
  difficulty: Difficulty
  variant: {
    id: number
    label: string
    changed_variant: boolean
  }
  policy: {
    id: number
    min_counted_commands: number
    max_counted_commands: number
    non_counted_patterns: string[]
  }
  counts: {
    counted_action_total: number
    non_counted_diagnostic_total: number
    remaining_counted_commands: number
    total_attempts: number
  }
  scaffolding: {
    live_dag: boolean
    expected_state: boolean
    contextual_feedback: boolean
  }
  repository_state: RepositorySnapshot
  expected_state: Pick<RepositorySnapshot, 'commits' | 'branches' | 'head'> | null
  review_mode: boolean
}

export type CommandResponse = {
  session: ScenarioSession
  step: {
    id: number
    terminal_output: string
    evaluation_result: string
    command_classification: string
    contextual_feedback: string
  }
}

export type TerminalLine = {
  id: string
  kind: 'system' | 'input' | 'output' | 'warning' | 'success'
  text: string
}
