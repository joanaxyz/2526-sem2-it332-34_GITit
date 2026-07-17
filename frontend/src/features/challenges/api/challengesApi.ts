import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  ChallengeRun,
  CommandFormPreview,
} from '@/features/challenges/types'

export const challengesApi = {
  commandFormPreview(formId: number) {
    return apiOperationRequest<'command_forms_preview_retrieve', CommandFormPreview>(
      'command_forms_preview_retrieve',
      `/command-forms/${formId}/preview/`,
    )
  },
  startChallengeRun(trialId: number, input?: { prior_run_id?: number | null; replay?: boolean }) {
    const body = {
      source_entry_point: 'level_page',
      prior_run_id: input?.prior_run_id ?? null,
      replay: input?.replay ?? false,
    } as ApiRequestBody<'challenge_trials_runs_create'>
    return apiOperationRequest<'challenge_trials_runs_create', ChallengeRun>(
      'challenge_trials_runs_create',
      `/challenge-trials/${trialId}/runs/`,
      { body },
    )
  },
  retryChallengeRun(runId: number) {
    return apiOperationRequest<'challenge_runs_retry_create', ChallengeRun>(
      'challenge_runs_retry_create',
      `/challenge-runs/${runId}/retry/`,
    )
  },
  discardChallengeRun(runId: number, options?: Omit<RequestInit, 'method' | 'body'>) {
    return apiOperationRequest<'challenge_runs_destroy', null>(
      'challenge_runs_destroy',
      `/challenge-runs/${runId}/`,
      options,
    )
  },
}
