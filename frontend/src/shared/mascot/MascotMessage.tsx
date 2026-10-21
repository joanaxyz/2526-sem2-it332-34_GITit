import type { ReactNode } from 'react'
import { GuideCharacterPortrait } from './GuideCharacterPortrait'
import './message.css'

/** One speaker and one speech bubble across setup, tours, and lessons. */
export function MascotMessage({ children, className = '', showSpeaker = true }: { children: ReactNode; className?: string; showSpeaker?: boolean }) {
  return <div className={`mascot-message ${showSpeaker ? '' : 'mascot-message--no-speaker'} ${className}`}>
    {showSpeaker ? <div className="mascot-message__sender">
      <GuideCharacterPortrait alt="Learning guide" />
      <span aria-hidden="true">Guide</span>
    </div> : null}
    <div className="mascot-message__bubble">{children}</div>
  </div>
}
