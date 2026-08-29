function gitTokens(command: string): string[] {
  return command.trim().toLowerCase().split(/\s+/).filter(Boolean)
}

/** Command family for the effect registry: "git commit -m x" -> "commit". */
function commandSkill(command: string): string {
  const tokens = gitTokens(command)
  if (tokens[0] !== 'git' || !tokens[1]) return 'default'
  return tokens[1]
}

function normalizeSkillName(skill: string | null | undefined): string | null {
  const value = skill?.trim().toLowerCase()
  if (!value) return null
  return value.startsWith('git ') ? commandSkill(value) : value
}

/** Exact effect-sheet key for a concrete command form. */
export function skillForCommand(command: string, fallbackSkill?: string | null): string {
  const tokens = gitTokens(command)
  if (tokens[0] === 'git') {
    if (tokens[1] === 'checkout' && (tokens.includes('--ours') || tokens.includes('--theirs'))) {
      return 'checkout-conflict'
    }
    if (tokens[1] === 'diff' && (tokens.includes('--ours') || tokens.includes('--theirs') || tokens.includes('--base'))) {
      return 'diff-conflict'
    }
  }
  return normalizeSkillName(fallbackSkill) ?? commandSkill(command)
}
