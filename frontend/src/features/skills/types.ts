// A command-skill the player has learned (their "spellbook"). Learned = the
// command's Command Adventure has been passed; derived server-side from the
// same pass milestone that unlocks challenges.
export type LearnedSkill = {
  id: number
  slug: string
  base_command: string
  title: string
  summary: string
  storey_id: number
  storey_number: number
  storey_title: string
}
