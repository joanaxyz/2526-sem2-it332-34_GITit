import { challengeScene } from '@/features/challenges/components/challengeWorkspaceLayout'
import type { ChallengeRun } from '@/features/challenges/types'
import type { BattleAssetManifest } from '@/shared/battle/battleAssets'
import { useBattleAssetGate } from '@/shared/battle/hooks/useBattleAssetGate'
import { workspaceRunAssetManifest } from '@/shared/level/workspace/workspaceBattle'

export function challengeRunAssetManifest(run: ChallengeRun, companionSlug: string): BattleAssetManifest {
  return workspaceRunAssetManifest(run, challengeScene(run).battle, companionSlug)
}

/** Hold the trial's entry until its battle roster and companion are decoded. */
export function useChallengeRunAssets({
  run,
  companionSlug,
  enabled,
}: {
  run: ChallengeRun | null | undefined
  companionSlug: string
  enabled: boolean
}): boolean {
  return useBattleAssetGate({
    entryKey: run ? `challenge:${run.id}:${companionSlug}` : null,
    enabled,
    buildManifest: () => (run ? challengeRunAssetManifest(run, companionSlug) : null),
  })
}
