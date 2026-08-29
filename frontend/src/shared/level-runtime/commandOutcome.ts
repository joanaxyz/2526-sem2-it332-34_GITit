/** Neutral result returned after a Git command is evaluated. */
export type CommandSubmissionOutcome = {
  processed: boolean
  counted: boolean
  solved: boolean
  failed: boolean
  command_family: string
  previous_rules_passing: number
  rules_passing: number
  rules_delta: number
  total_rules: number
  max_counted_commands: number
  counted_command_count: number
  remaining_counted_commands: number
}
