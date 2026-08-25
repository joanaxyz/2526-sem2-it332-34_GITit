import { BookOpen, RefreshCcw, X } from 'lucide-react'

import gitLogoImage from '@/assets/images/GIT_logo.png'
import type { AdventureRun } from '@/features/adventures/types'
import { AudioControls } from '@/shared/audio/AudioControls'
import { WorkspaceHeaderAccount } from '@/shared/level/components/WorkspaceHeaderAccount'

export function AdventureStatusHeader({
  run,
  isExiting,
  isRetrying,
  onExit,
  onRetry,
  onStartOver,
  onOpenLibrary,
}: {
  run: AdventureRun
  isExiting: boolean
  isRetrying: boolean
  onExit: () => void
  onRetry: () => void
  onStartOver: () => void
  onOpenLibrary: () => void
}) {
  const exitLabel = run.status === 'started' ? 'Exit' : 'Back'
  const canRetry = !run.replay && run.status === 'failed'
  const canStartOver = !run.replay && run.status === 'started'
  const canReplay = run.replay
  const replayLabel = run.status === 'started' ? 'Start over' : 'Play again'
  const replayIsStartOver = replayLabel === 'Start over'
  const replayActionLabel = isRetrying ? 'Starting' : replayLabel
  const guideLabel = run.library_opened
    ? 'Open the command guide. Score penalty already applied.'
    : "Open the command guide. Lowers this run's score by one star."
  const startOverLabel = isRetrying ? 'Starting over' : 'Start over'

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
        <span>Adventure · Wave {Math.max(1, run.current_wave)} / {Math.max(1, run.total_waves)}</span>
        <strong>{run.selected_level?.title ?? run.current_attempt?.level.title ?? 'Adventure run'}</strong>
      </div>

      <span className="gameplay-header-spacer" aria-hidden="true" />

      <AudioControls
        className="gameplay-header-audio-controls"
        buttonClassName="gameplay-header-button gameplay-header-icon-button gameplay-header-audio"
      />

      <button
        type="button"
        className="gameplay-header-button gameplay-header-icon-button"
        title={guideLabel}
        aria-label={guideLabel}
        onClick={onOpenLibrary}
      >
        <BookOpen aria-hidden="true" />
      </button>
      {canRetry ? (
        <button type="button" className="gameplay-header-button" disabled={isRetrying} onClick={onRetry}>
          <RefreshCcw aria-hidden="true" />
          {isRetrying ? 'Starting retry' : 'Retry'}
        </button>
      ) : null}
      {canStartOver ? (
        <button
          type="button"
          className="gameplay-header-button gameplay-header-icon-button"
          disabled={isRetrying}
          title={startOverLabel}
          aria-label={startOverLabel}
          onClick={onStartOver}
        >
          <RefreshCcw aria-hidden="true" />
        </button>
      ) : null}
      {canReplay ? (
        <button
          type="button"
          className={`gameplay-header-button${replayIsStartOver ? ' gameplay-header-icon-button' : ''}`}
          disabled={isRetrying}
          title={replayActionLabel}
          aria-label={replayActionLabel}
          onClick={onRetry}
        >
          <RefreshCcw aria-hidden="true" />
          {replayIsStartOver ? null : replayActionLabel}
        </button>
      ) : null}

      <WorkspaceHeaderAccount />
    </header>
  )
}
