// Single-letter chars inside combined flags (e.g. -dv) that indicate a branch mutation.
const BRANCH_MUTATION_SINGLE_CHARS = new Set(['d', 'D', 'm', 'M', 'c', 'C', 'u', 't'])

// Long-form flags that mutate the branch list.
const BRANCH_MUTATION_LONG_FLAGS = new Set([
  '--delete',
  '--force',
  '--move',
  '--copy',
  '--set-upstream-to',
  '--unset-upstream',
  '--story',
  '--no-story',
])

function classifyBranchArgs(args: string[]): 'diagnostic' | 'action' {
  for (const arg of args) {
    if (!arg.startsWith('-')) return 'action' // positional = branch name = create/rename

    if (arg.startsWith('--')) {
      // Long-form flag: check for exact mutation flag or --set-upstream-to=... style
      const base = arg.includes('=') ? arg.slice(0, arg.indexOf('=')) : arg
      if (BRANCH_MUTATION_LONG_FLAGS.has(base)) return 'action'
    } else {
      // Short-form: each char after the dash is a flag letter
      for (const ch of arg.slice(1)) {
        if (BRANCH_MUTATION_SINGLE_CHARS.has(ch)) return 'action'
      }
    }
  }
  return 'diagnostic'
}

export function classifyCommand(rawInput: string): 'diagnostic' | 'action' {
  const trimmed = rawInput.trim()
  const lower = trimmed.toLowerCase()

  if (!lower.startsWith('git ') && lower !== 'git') return 'action'

  const tokens = trimmed.split(/\s+/)
  const sub = (tokens[1] ?? '').toLowerCase()

  if (sub === 'status') return 'diagnostic'
  if (sub === 'log') return 'diagnostic'
  if (sub === 'reflog') return 'diagnostic'
  if (sub === 'diff') return 'diagnostic'

  if (sub === 'branch') {
    return classifyBranchArgs(tokens.slice(2))
  }

  return 'action'
}
