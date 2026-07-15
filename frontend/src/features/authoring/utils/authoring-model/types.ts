import type { BattleStageConfig, ContentKind, Visibility } from '@/features/authoring/types'

export type AuthoredVariant = {
  slug: string
  label: string
  initialStateText: string
  solutionCommands: string[]
}

/** One playable problem: a wave (adventure) or a difficulty trial (challenge). */
export type AuthoredProblem = {
  slug: string
  title: string
  /** Challenge trials only. */
  difficulty: string
  /** The scenario story shown to the player (compiles to scenario_context). */
  story: string
  task: string
  solutionCommands: string[]
  initialStateText: string
  evaluationMode: string
  minCountedCommands: number
  maxCountedCommands: number
  variants: AuthoredVariant[]
}

export type AuthoredLevel = {
  slug: string
  title: string
  /** Short lesson intro shown above the level's problems. */
  brief: string
  /** CommandForm ids this level introduces AND reuses. Listing a form on several
   *  levels is the spiral: its mastery target counts the levels that exercise it. */
  commandForms: number[]
  problems: AuthoredProblem[]
}

export type BookBlock = { type: string; body: string }
export type BookPage = { title: string; blocks: BookBlock[] }

export type AuthoringForm = {
  kind: ContentKind
  slug: string
  title: string
  summary: string
  commandFamily: string
  difficulty: string
  tags: string[]
  visibility: Visibility
  chapterId: number | null
  // lesson
  pages: BookPage[]
  // playable
  levels: AuthoredLevel[]
  battleStage: BattleStageConfig
}
