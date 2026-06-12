import { apiRequest } from '@/shared/api/httpClient'
import type {
  CommandAdventureSummary,
  CommandFormPreview,
  CommandSkillSummary,
  StoreyContentPage,
  StoreyContentSection,
  ChallengeSummary,
  TomeSummary,
} from '@/features/challenges/types'
import type { ChallengeRun } from '@/shared/practice/types'

type StoreyContentResult<TSection extends StoreyContentSection> =
  TSection extends 'command_adventures'
    ? StoreyContentPage<CommandAdventureSummary>
    : TSection extends 'command_skills'
    ? StoreyContentPage<CommandSkillSummary>
    : TSection extends 'tomes'
    ? StoreyContentPage<TomeSummary>
    : StoreyContentPage<ChallengeSummary>

export const challengesApi = {
  storeyContent<TSection extends StoreyContentSection>(
    storeyId: number,
    section: TSection,
    options?: { cursor?: number | null; limit?: number },
  ) {
    const params = new URLSearchParams({ section })
    if (options?.cursor) params.set('cursor', String(options.cursor))
    if (options?.limit) params.set('limit', String(options.limit))
    return apiRequest<StoreyContentResult<TSection>>(
      `/storeys/${storeyId}/content/?${params.toString()}`,
    )
  },
  commandFormPreview(formId: number) {
    return apiRequest<CommandFormPreview>(`/command-forms/${formId}/preview/`)
  },
  startChallengeRun(questId: number, input?: { prior_run_id?: number | null; review?: boolean }) {
    return apiRequest<ChallengeRun>(`/challenge-quests/${questId}/runs/`, {
      method: 'POST',
      body: JSON.stringify({
        source_entry_point: input?.review ? 'review' : 'tower_page',
        prior_run_id: input?.prior_run_id ?? null,
        review: input?.review ?? false,
      }),
    })
  },
  retryChallengeRun(runId: number) {
    return apiRequest<ChallengeRun>(`/challenge-runs/${runId}/retry/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
  finishChallengeRun(runId: number) {
    return apiRequest<ChallengeRun>(`/challenge-runs/${runId}/finish/`, {
      method: 'POST',
      body: JSON.stringify({}),
    })
  },
}
