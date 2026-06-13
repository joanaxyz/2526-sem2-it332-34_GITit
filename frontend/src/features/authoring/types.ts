export type ContentKind = 'adventure' | 'challenge' | 'tome'
export type ContentStatus = 'draft' | 'testable' | 'published' | 'archived'
export type Visibility = 'private' | 'public' | 'store'

export type ValidationErrorRow = {
  field: string
  message: string
}

export type ContentDefinition = {
  id: number
  kind: ContentKind
  owner_id: number | null
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
