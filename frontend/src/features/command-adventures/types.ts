import type { RepositorySnapshot } from '@/shared/practice/types'

export type AdventureRunStatus = 'started' | 'completed' | 'failed' | 'abandoned'
export type AttemptStatus = 'started' | 'completed' | 'failed'

export type AdventureScaffolding = {
  live_dag: boolean
  expected_state: boolean
  contextual_feedback: boolean
  hints: boolean
}

export type AdventureCommandBudget = {
  min_counted_commands: number
  max_counted_commands: number
  ideal_counted_commands: number
}

export type AdventureAttemptCounts = {
  command_count: number
  counted_command_count: number
  hint_count: number
}

export type AdventureProblemRef = {
  id: number
  slug: string
  title: string
  summary: string
  is_required: boolean
}

export type AdventureStudentContext = {
  story?: string
  task?: string
  [key: string]: unknown
}

export type AdventureAttempt = {
  id: number
  order: number
  status: AttemptStatus
  problem: AdventureProblemRef
  variant: { id: number; label: string }
  student_context: AdventureStudentContext
  scaffolding: AdventureScaffolding
  command_budget: AdventureCommandBudget
  counts: AdventureAttemptCounts
  repository_state: RepositorySnapshot
}

export type AdventureAttemptResult = {
  id: number
  order: number
  status: AttemptStatus
  correctness_score: number
  efficiency_score: number
  independence_score: number
  final_score: number
  mastery_gain: number
  hint_count: number
  counted_command_count: number
}

export type AdventureRun = {
  id: number
  status: AdventureRunStatus
  command_adventure: { id: number; slug: string; title: string; description: string }
  current_problem_index: number
  total_problems: number
  total_score: number
  mastery_progress_gained: number
  completed_at: string | null
  current_attempt: AdventureAttempt | null
  results: AdventureAttemptResult[]
  progress: { completed: number; total: number }
}

export type AdventureHintResponse = {
  run: AdventureRun
  hint: string
  hint_number: number
}

export type AdventureCommandResponse = {
  run: AdventureRun
  solved: boolean
  stdout: string
  stderr: string
  exit_code: number
  terminal_output: string
  command_classification: string
}
