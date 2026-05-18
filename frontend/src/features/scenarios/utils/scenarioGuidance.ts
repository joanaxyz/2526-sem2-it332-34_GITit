export function commitMessageGuidance(taskPrompt: string) {
  const lower = taskPrompt.toLowerCase()

  if (lower.includes('message that mentions') || lower.includes('message must mention')) {
    return 'Commit message: include the word named in the task. That message rule is graded.'
  }
  if (lower.includes('no exact commit message') || lower.includes('message is not graded')) {
    return 'Commit message: exact wording is not graded for this level.'
  }
  if (lower.includes('commit')) {
    return 'Commit message: use a reasonable message; exact wording matters only when the task says it must mention a word.'
  }
  return 'Commit message: not part of this scenario unless the task asks for a commit.'
}
