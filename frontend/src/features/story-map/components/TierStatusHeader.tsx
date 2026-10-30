import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { CommandGuideLauncher } from '@/features/story-map/components/CommandGuideLauncher'
import { TierStatsBar } from '@/features/story-map/components/tier-workspace/TierStatsBar'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import type { RepoGraphTrigger } from '@/shared/level/workspace/types'
import { WorkspaceStatusHeader } from '@/shared/level/workspace/WorkspaceStatusHeader'

/** The adventure tier's command bar: its stats, the command guide, and run controls. */
export function TierStatusHeader({
  run,
  isExiting = false,
  onExit,
  onRetry,
  onStartOver,
  onReplay,
  commandGuides = [],
  currentCommandGuideKey,
  commandGuideOpen = false,
  onSelectCommandGuide,
  repoGraph,
}: {
  run: TierRun
  isExiting?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onReplay?: () => void
  commandGuides?: readonly CommandIntroduction[]
  currentCommandGuideKey?: string | null
  commandGuideOpen?: boolean
  onSelectCommandGuide?: (teachingKey: string) => void
  repoGraph?: RepoGraphTrigger
}) {
  const scored = !run.transfer && !run.replay

  return (
    <WorkspaceStatusHeader
      label="Adventure command bar"
      missionLabel="Current adventure"
      title={run.tier.adventure_level_title}
      note={run.transfer ? 'Transfer checkpoint · first attempt recorded' : null}
      stats={<TierStatsBar run={run} repoGraph={repoGraph} />}
      guide={!run.transfer ? (
        <CommandGuideLauncher
          guides={commandGuides}
          currentGuideKey={currentCommandGuideKey}
          guideOpen={commandGuideOpen}
          onSelectGuide={onSelectCommandGuide ?? (() => undefined)}
        />
      ) : null}
      status={run.status}
      isExiting={isExiting}
      onExit={onExit}
      onRetry={scored && run.status === 'failed' ? onRetry : undefined}
      onStartOver={scored && run.status === 'started' ? onStartOver : undefined}
      onReplay={run.replay ? onReplay : undefined}
    />
  )
}
