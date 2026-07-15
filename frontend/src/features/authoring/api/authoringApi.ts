import { apiRequest } from '@/shared/api/httpClient'
import type {
  AuthoringChapter,
  AuthoringChapterInput,
  AuthoringChapterList,
  ContentDefinition,
  ContentDefinitionList,
  ContentKind,
  TestRunResult,
  ValidationResult,
  Visibility,
} from '@/features/authoring/types'

export type ContentDefinitionInput = {
  kind: ContentKind
  visibility?: Visibility
  slug: string
  title: string
  summary?: string
  tags?: string[]
  command_family?: string
  difficulty?: string
  chapter?: number | null
  definition?: Record<string, unknown>
}

export type CommandFormOption = {
  id: number
  slug: string
  usage_form: string
  label: string
  skill_slug: string
  skill_title: string
  base_command: string
  chapter_number: number | null
}

export const authoringApi = {
  chapters() {
    return apiRequest<AuthoringChapterList>('/authoring/chapters/')
  },
  createChapter(input: AuthoringChapterInput) {
    return apiRequest<AuthoringChapter>('/authoring/chapters/', { method: 'POST', body: JSON.stringify(input) })
  },
  updateChapter(id: number, input: AuthoringChapterInput) {
    return apiRequest<AuthoringChapter>(`/authoring/chapters/${id}/`, { method: 'PATCH', body: JSON.stringify(input) })
  },
  deleteChapter(id: number) {
    return apiRequest<null>(`/authoring/chapters/${id}/`, { method: 'DELETE' })
  },
  list(kind?: ContentKind) {
    const suffix = kind ? `?kind=${encodeURIComponent(kind)}` : ''
    return apiRequest<ContentDefinitionList>(`/authoring/content-definitions/${suffix}`)
  },
  get(id: number) {
    return apiRequest<ContentDefinition>(`/authoring/content-definitions/${id}/`)
  },
  create(input: ContentDefinitionInput) {
    return apiRequest<ContentDefinition>('/authoring/content-definitions/', {
      method: 'POST',
      body: JSON.stringify(input),
    })
  },
  update(id: number, input: Partial<ContentDefinitionInput>) {
    return apiRequest<ContentDefinition>(`/authoring/content-definitions/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(input),
    })
  },
  validate(id: number) {
    return apiRequest<ValidationResult>(`/authoring/content-definitions/${id}/validate/`, {
      method: 'POST',
    })
  },
  publish(id: number) {
    return apiRequest<ContentDefinition>(`/authoring/content-definitions/${id}/publish/`, {
      method: 'POST',
    })
  },
  testRun(id: number) {
    return apiRequest<TestRunResult>(`/authoring/content-definitions/${id}/test-run/`, {
      method: 'POST',
    })
  },
  commandForms() {
    return apiRequest<{ results: CommandFormOption[] }>('/authoring/command-forms/')
  },
}
