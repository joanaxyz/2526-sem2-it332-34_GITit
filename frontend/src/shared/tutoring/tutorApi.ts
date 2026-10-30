import type { ApiRequestBody, ApiSchemas } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'

export type TutorContext = ApiRequestBody<'tutor_chat'>['context']
export type TutorReply = ApiSchemas['TutorChatResponse']

export const tutorApi = {
  chat(body: ApiRequestBody<'tutor_chat'>, signal: AbortSignal) {
    return apiOperationRequest<'tutor_chat', TutorReply>('tutor_chat', '/tutoring/chat/', { body, signal })
  },
}
