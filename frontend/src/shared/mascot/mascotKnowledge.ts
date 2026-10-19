export type MascotKnowledgeTip = {
  id: string
  command?: string
  text: string
  source: string
}

/** Safe starting points before the learner has earned any command skills. */
export const INTRODUCTORY_TIPS: readonly MascotKnowledgeTip[] = [
  { id: 'basics:history', source: 'Git basics', text: 'Git keeps a history of your project. Each saved snapshot lets you see what changed over time.' },
  { id: 'basics:practice', source: 'Getting started', text: 'Adventures let you practice Git in a simulated repository. You can experiment here without changing files on your computer.' },
  { id: 'basics:state', source: 'Git basics', text: 'Before making a move, look at the repository and the goal. Understanding what needs to change helps you choose your next command.' },
]

/** Prefer above the character; use the space below a topmost ledge when needed. */
export function mascotSpeechPosition(x: number, feet: number, width: number, height: number, viewportWidth: number, viewportHeight: number) {
  const gap = 12
  const left = Math.max(gap, Math.min(viewportWidth - width - gap, x - width / 2))
  const above = feet - 100 - height - gap
  const below = above < gap
  const top = Math.max(gap, Math.min(viewportHeight - height - gap, below ? feet + gap : above))
  return { left, top, below, tail: Math.max(20, Math.min(width - 20, x - left)) }
}
