import type { ReactNode } from 'react'
import { GuideCharacterPortrait } from './GuideCharacterPortrait'
import './message.css'

/** One speaker and one speech bubble across setup, tours, and lessons. */
export function MascotMessage({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`mascot-message ${className}`}>
    <div className="mascot-message__sender">
      <GuideCharacterPortrait alt="Learning guide" />
      <span aria-hidden="true">Guide</span>
    </div>
    <div className="mascot-message__bubble">{children}</div>
  </div>
}
