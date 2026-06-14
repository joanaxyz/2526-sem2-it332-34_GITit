export type ContentKind = 'adventure' | 'challenge' | 'tome'
export type ContentStatus = 'draft' | 'testable' | 'published' | 'archived'
export type Visibility = 'private' | 'public' | 'store'

export type ValidationErrorRow = {
  field: string
  message: string
}

export type ChestRewardRow = { threshold: number; coins: number }

/** One authored battle-stage prop. Coordinates are normalized (0..1). */
export type BattleStageArtifactConfig = {
  slug: string
  x: number
  y: number
  scale: number
  rotation: number
  z: number
}

/** Authored battle-stage dressing for a storey (backdrop slug + props). */
export type BattleStageConfig = {
  background: string | null
  artifacts: BattleStageArtifactConfig[]
}

/** A user-authored storey (floor): groups 1 adventure + 1+ challenges/tomes. */
export type AuthoringStorey = {
  id: number
  owner_id: number | null
  slug: string
  title: string
  summary: string
  sort_order: number
  chest_rewards: ChestRewardRow[]
  mob_roster: string[]
  boss_roster: string[]
  pass_bar_fraction: number
  battle_stage?: BattleStageConfig
  created_at: string
  updated_at: string
}

export type AuthoringStoreyList = {
  results: AuthoringStorey[]
}

export type AuthoringStoreyInput = {
  title?: string
  slug?: string
  summary?: string
  sort_order?: number
  chest_rewards?: ChestRewardRow[]
  mob_roster?: string[]
  boss_roster?: string[]
  pass_bar_fraction?: number
  battle_stage?: BattleStageConfig
}

export type ContentDefinition = {
  id: number
  kind: ContentKind
  owner_id: number | null
  storey_id: number | null
  source_definition_id: number | null
  visibility: Visibility
  status: ContentStatus
  slug: string
  title: string
  summary: string
  tags: string[]
  command_family: string
  difficulty: string
  definition?: Record<string, unknown>
  validation_errors: ValidationErrorRow[]
  published_at: string | null
  created_at: string
  updated_at: string
}

export type ContentDefinitionList = {
  results: ContentDefinition[]
}

export type ValidationResult = {
  valid: boolean
  errors: ValidationErrorRow[]
}

export type TestRunResult = {
  kind: ContentKind
  runtime_id: number | null
  start_path?: string | null
  pages?: unknown[]
}
