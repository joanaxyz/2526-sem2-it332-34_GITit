import type { ReactNode } from 'react'
import { GuideCharacterPortrait } from './GuideCharacterPortrait'
import './message.css'

/** One speaker and one speech bubble across setup, tours, and lessons. */
export function MascotMessage({ children, className = '', showSpeaker = true, onSpeakerClick, speakerLabel, speakerActions }: {
  children: ReactNode
  className?: string
  showSpeaker?: boolean
  onSpeakerClick?: () => void
  speakerLabel?: string
  speakerActions?: ReactNode
}) {
  return <div className={`mascot-message ${showSpeaker ? '' : 'mascot-message--no-speaker'} ${className}`}>
    {showSpeaker ? <div className="mascot-message__sender">
      {onSpeakerClick ? <button type="button" className="mascot-message__speaker-button"
        aria-label={speakerLabel} title={speakerLabel} onClick={onSpeakerClick}>
        <GuideCharacterPortrait alt="Learning guide" />
      </button> : <GuideCharacterPortrait alt="Learning guide" />}
      <span aria-hidden="true">Guide</span>
      {speakerActions}
    </div> : null}
    <div className="mascot-message__bubble">{children}</div>
  </div>
}
