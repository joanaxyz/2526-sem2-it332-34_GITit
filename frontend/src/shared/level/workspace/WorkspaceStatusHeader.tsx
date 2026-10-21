import { RefreshCcw, X } from 'lucide-react'
import type { ReactNode } from 'react'

import gitLogoImage from '@/assets/images/g34-icon.webp'
import { AudioControls } from '@/shared/audio/AudioControls'

/**
 * The gameplay command bar: exit, brand, the level title, the stats strip,
 * audio, an optional guide launcher, and whichever run controls the caller
 * offers. Callers decide which controls apply; a missing handler hides it.
 */
export function WorkspaceStatusHeader({
  label,
  missionLabel,
  title,
  note,
  stats,
  guide,
  status,
  isExiting = false,
  busy = false,
  onExit,
  onRetry,
  onStartOver,
  onReplay,
}: {
  /** Accessible name of the bar, e.g. "Adventure command bar". */
  label: string
  /** Accessible name of the title block, e.g. "Current adventure". */
  missionLabel: string
  title: string
  note?: string | null
  stats: ReactNode
  guide?: ReactNode
  status: string
  isExiting?: boolean
  /** A fresh attempt is being prepared: run controls wait for it. */
  busy?: boolean
  onExit?: () => void
  onRetry?: () => void
  onStartOver?: () => void
  onReplay?: () => void
}) {
  const exitLabel = status === 'started' ? 'Exit' : 'Back'
  const replayLabel = status === 'started' ? 'Start over' : 'Play again'
  const replayIsStartOver = replayLabel === 'Start over'
  const replayActionLabel = busy ? 'Starting' : replayLabel
  const startOverLabel = busy ? 'Starting over' : 'Start over'

  return (
    <header className="gameplay-workspace-header" aria-label={label}>
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
        <span>IT it!</span>
      </a>

      <div className="gameplay-header-mission" aria-label={missionLabel}>
        {/* The title gives way to the stats strip, so its full text stays on hover. */}
        <strong title={title}>{title}</strong>
        {note ? <span>{note}</span> : null}
      </div>

      <span className="gameplay-header-spacer" aria-hidden="true" />

      {stats}

      <AudioControls
        className="gameplay-header-audio-controls"
        buttonClassName="gameplay-header-button gameplay-header-icon-button gameplay-header-audio"
      />

      {guide}

      {onRetry ? (
        <button type="button" className="gameplay-header-button" disabled={busy} onClick={onRetry}>
          <RefreshCcw aria-hidden="true" />
          {busy ? 'Starting retry' : 'Retry'}
        </button>
      ) : null}
      {onStartOver ? (
        <button
          type="button"
          className="gameplay-header-button gameplay-header-icon-button"
          disabled={busy}
          title={startOverLabel}
          aria-label={startOverLabel}
          onClick={onStartOver}
        >
          <RefreshCcw aria-hidden="true" />
        </button>
      ) : null}
      {onReplay ? (
        <button
          type="button"
          className={`gameplay-header-button${replayIsStartOver ? ' gameplay-header-icon-button' : ''}`}
          disabled={busy}
          title={replayActionLabel}
          aria-label={replayActionLabel}
          onClick={onReplay}
        >
          <RefreshCcw aria-hidden="true" />
          {replayIsStartOver ? null : replayActionLabel}
        </button>
      ) : null}
    </header>
  )
}
