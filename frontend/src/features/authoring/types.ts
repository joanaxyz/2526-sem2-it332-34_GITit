import type { StageLanding } from '@/shared/battle/types'

export type ContentKind = 'adventure' | 'challenge' | 'lesson'
export type ContentStatus = 'draft' | 'testable' | 'published' | 'archived'
export type Visibility = 'private' | 'public' | 'store'

type ValidationErrorRow = {
  field: string
  message: string
}

/** Authored battle-stage for one playable content definition: a backdrop (the
 *  asset itself knows whether it's a still image or a spritesheet) plus an
 *  optional `landing` — the platform the fighters stand on, dragged and resized
 *  on the editor preview and stored in normalized 0..1 coordinates. */
export type BattleStageConfig = {
  background: string | null
  landing: StageLanding | null
}

/** A user-authored chapter (floor): groups 1 adventure + 1+ challenges/lessons. */
export type AuthoringChapter = {
  id: number
  owner_id: number | null
  slug: string
  title: string
  summary: string
  sort_order: number
  created_at: string
  updated_at: string
}

export type AuthoringChapterList = {
  results: AuthoringChapter[]
}

export type AuthoringChapterInput = {
  title?: string
  slug?: string
  summary?: string
  sort_order?: number
}

export type ContentDefinition = {
  id: number
  kind: ContentKind
  owner_id: number | null
  chapter_id: number | null
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
