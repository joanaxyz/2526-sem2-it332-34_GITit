export const DEFAULT_DIFFICULTY_ORDER = ['easy', 'medium', 'hard'] as const

export type KnownDifficulty = (typeof DEFAULT_DIFFICULTY_ORDER)[number]
