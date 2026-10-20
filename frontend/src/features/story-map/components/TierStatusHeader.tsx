import { RefreshCcw, X } from 'lucide-react'

import gitLogoImage from '@/assets/images/g34-icon.webp'
import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'
import { CommandGuideLauncher } from '@/features/story-map/components/CommandGuideLauncher'
import { TierStatsBar } from '@/features/story-map/components/tier-workspace/TierStatsBar'
import type { RepoGraphTrigger } from '@/features/story-map/components/tier-workspace/TierStatsBar'
import { AudioControls } from '@/shared/audio/AudioControls'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'

/** Mirrors ChallengeStatusHeader for the adventure-tier run lifecycle. */
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
  const exitLabel = run.status === 'started' ? 'Exit' : 'Back'
  const canRetry = !run.transfer && !run.replay && run.status === 'failed' && !!onRetry
  const canStartOver = !run.transfer && !run.replay && run.status === 'started' && !!onStartOver
  const canReplay = run.replay && !!onReplay
  const replayLabel = run.status === 'started' ? 'Start over' : 'Play again'
  const replayIsStartOver = replayLabel === 'Start over'

  return (
    <header className="gameplay-workspace-header" aria-label="Adventure command bar">
      <button
        type="button"
        className="gameplay-header-close"
        disabled={isExiting}
        title={exitLabel}
        aria-label={isExiting ? 'Exiting' : exitLabel}
        onClick={onExit}
      >
        <X aria-hidden="true" />
      </button>

      <a className="gameplay-header-brand" href="/home" aria-label="GIT it! home">
        <img src={gitLogoImage} alt="" />
        <span>GIT it!</span>
      </a>

      <div className="gameplay-header-mission" aria-label="Current adventure">
        <strong>{run.tier.adventure_level_title}</strong>
        {run.transfer ? <span>Transfer checkpoint · first attempt recorded</span> : null}
      </div>

      <span className="gameplay-header-spacer" aria-hidden="true" />

      <TierStatsBar run={run} repoGraph={repoGraph} />

      <AudioControls
        className="gameplay-header-audio-controls"
        buttonClassName="gameplay-header-button gameplay-header-icon-button gameplay-header-audio"
      />

      {!run.transfer ? <CommandGuideLauncher
        guides={commandGuides}
        currentGuideKey={currentCommandGuideKey}
        guideOpen={commandGuideOpen}
        onSelectGuide={onSelectCommandGuide ?? (() => undefined)}
      /> : null}

      {canRetry ? (
        <button type="button" className="gameplay-header-button" onClick={onRetry}>
          <RefreshCcw aria-hidden="true" />
          Retry
        </button>
      ) : null}
      {canStartOver ? (
        <button
          type="button"
          className="gameplay-header-button gameplay-header-icon-button"
          title="Start over"
          aria-label="Start over"
          onClick={onStartOver}
        >
          <RefreshCcw aria-hidden="true" />
        </button>
      ) : null}
      {canReplay ? (
        <button
          type="button"
          className={`gameplay-header-button${replayIsStartOver ? ' gameplay-header-icon-button' : ''}`}
          title={replayLabel}
          aria-label={replayLabel}
          onClick={onReplay}
        >
          <RefreshCcw aria-hidden="true" />
          {replayIsStartOver ? null : replayLabel}
        </button>
      ) : null}
    </header>
  )
}
