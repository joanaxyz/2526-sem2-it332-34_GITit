import type { ApiRequestBody } from '@/shared/api/generated/apiTypes'
import { apiOperationRequest } from '@/shared/api/httpClient'
import type {
  ChallengeRun,
  AdventureSummary,
  CommandFormPreview,
  CommandSkillSummary,
  ChapterContentPage,
  ChapterContentSection,
  ChallengeSummary,
  ChapterLessonSummary,
} from '@/features/challenges/types'

type ChapterContentResult<TSection extends ChapterContentSection> =
  TSection extends 'adventures'
    ? ChapterContentPage<AdventureSummary>
    : TSection extends 'command_skills'
    ? ChapterContentPage<CommandSkillSummary>
    : TSection extends 'lessons'
    ? ChapterContentPage<ChapterLessonSummary>
    : ChapterContentPage<ChallengeSummary>

export const challengesApi = {
  chapterContent<TSection extends ChapterContentSection>(
    chapterId: number,
    section: TSection,
    options?: { cursor?: number | null; limit?: number },
  ) {
    const params = new URLSearchParams({ section })
    if (options?.cursor) params.set('cursor', String(options.cursor))
    if (options?.limit) params.set('limit', String(options.limit))
    return apiOperationRequest<'chapters_content_retrieve', ChapterContentResult<TSection>>(
      'chapters_content_retrieve',
      `/chapters/${chapterId}/content/?${params.toString()}`,
    )
  },
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
