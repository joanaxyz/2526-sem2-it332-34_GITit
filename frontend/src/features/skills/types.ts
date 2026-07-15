// A command-skill the player has learned (their "spellbook"). Learned = the
// player has solved with one of the skill's command forms at least once.
export type LearnedSkill = {
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  chapter_id: number
  chapter_number: number
  chapter_title: string
}
