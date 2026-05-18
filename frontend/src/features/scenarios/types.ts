export type Difficulty = 'easy' | 'medium' | 'hard'
export type DifficultyStatus = 'available' | 'locked' | 'in_progress' | 'complete'

export type CommandPolicy = {
  id: number
  min_counted_commands: number
  max_counted_commands: number
  non_counted_patterns: string[]
}

export type DifficultyAccess = {
  id: number
  difficulty: Difficulty
  narrative: string
  task_prompt: string
  status: DifficultyStatus
  review_available: boolean
  active_session_id: number | null
  policy: CommandPolicy
  completion: null | {
    first_attempt_star: boolean
    counted_action_total: number
    completed_at: string
  }
}

export type ScenarioSkillFocus = {
  id: number
  slug: string
  title: string
  focus: string
  narrative: string
  task_prompt: string
  learning_unit_id: number
  lesson_id: number
  difficulties: DifficultyAccess[]
}
