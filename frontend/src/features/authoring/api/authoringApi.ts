import { apiOperationRequest, apiRequest } from '@/shared/api/httpClient'
import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import type {
  AuthoringChapter,
  AuthoringChapterInput,
  AuthoringChapterList,
  ContentDefinition,
  ContentDefinitionList,
  ContentKind,
  CommandFormOption,
  TestRunResult,
  ValidationResult,
} from '@/features/authoring/types'

export type ContentDefinitionInput =
  ApiRequestBody<'authoring_content_definitions_create'>

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
    return apiOperationRequest(
      'authoring_content_definitions_create',
      '/authoring/content-definitions/',
      { body: input },
    ) as Promise<ContentDefinition>
  },
  update(
    id: number,
    input: ApiRequestBody<'authoring_content_definitions_partial_update'>,
  ) {
    return apiOperationRequest(
      'authoring_content_definitions_partial_update',
      `/authoring/content-definitions/${id}/`,
      { body: input },
    ) as Promise<ContentDefinition>
  },
  validate(id: number) {
    return apiOperationRequest(
      'authoring_content_definitions_validate_create',
      `/authoring/content-definitions/${id}/validate/`,
    ) as Promise<ValidationResult>
  },
  publish(id: number) {
    return apiOperationRequest(
      'authoring_content_definitions_publish_create',
      `/authoring/content-definitions/${id}/publish/`,
    ) as Promise<ContentDefinition>
  },
  testRun(id: number) {
    return apiOperationRequest(
      'authoring_content_definitions_test_run_create',
      `/authoring/content-definitions/${id}/test-run/`,
    ) as Promise<TestRunResult>
  },
  commandForms() {
    return apiRequest<{ results: CommandFormOption[] }>('/authoring/command-forms/')
  },
}
