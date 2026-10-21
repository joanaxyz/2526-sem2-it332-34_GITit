import { queryKeys } from '@/shared/api/queryKeys'
import type { WorkspaceScene } from '@/shared/level/workspace/types'
import { storyPathWithQuery } from '@/shared/navigation/routes'
import type { ChallengeRun } from '@/features/challenges/types'

/** Where a Challenge Gate run sits, for the shared gameplay workspace. */
export function challengeScene(run: Pick<ChallengeRun, 'id' | 'challenge'>): WorkspaceScene {
  return {
    title: run.challenge.title,
    rootName: run.challenge.slug,
    runQueryKey: queryKeys.challengeRun(run.id),
    // `level_id` is the trial; `id` is the gate.
    battle: { stageKey: `challenge:${run.challenge.level_id}`, levelKey: `challenge:${run.challenge.id}` },
  }
}

export function mapUrlForRun(run: Pick<ChallengeRun, 'chapter' | 'story'>) {
  return storyPathWithQuery(run.story?.slug, `chapter=${run.chapter.id}`)
}
