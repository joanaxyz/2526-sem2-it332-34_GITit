/**
 * Where each companion keeps its git-skill spell assets: the animated attack
 * sheets used in battle AND the static `portrait/<command>.png` previews used
 * in the story map's Skill Reward panel. One source of truth so the two never
 * drift (the battle effect registry imports these same roots).
 */
export const SKILL_EFFECT_ROOTS: Record<string, string> = {
  blue: '/cosmetics/companion/blue/effects/skill-flames-25',
  black: '/cosmetics/companion/black/effects/skill-lightning-25',
  white: '/cosmetics/companion/white/effects/skill-ice-25',
}

export const DEFAULT_SKILL_COMPANION = 'blue'

function rootForCompanion(companionSlug: string | null | undefined): string {
  const slug = companionSlug?.trim().toLowerCase() || DEFAULT_SKILL_COMPANION
  return SKILL_EFFECT_ROOTS[slug] ?? SKILL_EFFECT_ROOTS[DEFAULT_SKILL_COMPANION]
}

/**
 * The command-family key used by the spell asset filenames (`init`, `add`,
 * `commit`, ...). A level's `command` can be a comma-separated workflow
 * ("git status, git diff"); the reward is keyed off the primary command.
 */
function skillCommandFamily(command: string): string {
  const primary = command.split(',')[0]?.trim().toLowerCase() ?? ''
  return primary.replace(/^git\s+/, '').trim()
}

/** The primary git command a level teaches, e.g. "git status". */
export function primarySkillCommand(command: string): string {
  return command.split(',')[0]?.trim() ?? command.trim()
}

/**
 * Static portrait preview of the equipped companion's spell for a git command,
 * e.g. `/cosmetics/companion/white/effects/skill-ice-25/portrait/init.png`.
 */
export function companionSkillPortrait(
  companionSlug: string | null | undefined,
  command: string,
): string {
  const family = skillCommandFamily(command) || 'default'
  return `${rootForCompanion(companionSlug)}/portrait/${family}.png`
}
