import { apiRequest } from '@/shared/api/httpClient'
import type {
  AuthoringStorey,
  AuthoringStoreyInput,
  AuthoringStoreyList,
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
  storey?: number | null
  definition?: Record<string, unknown>
}

export const authoringApi = {
  storeys() {
    return apiRequest<AuthoringStoreyList>('/authoring/storeys/')
  },
  createStorey(input: AuthoringStoreyInput) {
    return apiRequest<AuthoringStorey>('/authoring/storeys/', { method: 'POST', body: JSON.stringify(input) })
  },
  updateStorey(id: number, input: AuthoringStoreyInput) {
    return apiRequest<AuthoringStorey>(`/authoring/storeys/${id}/`, { method: 'PATCH', body: JSON.stringify(input) })
  },
  deleteStorey(id: number) {
    return apiRequest<null>(`/authoring/storeys/${id}/`, { method: 'DELETE' })
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
}
