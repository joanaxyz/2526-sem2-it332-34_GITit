import type { ReactNode } from 'react'
import './message.css'

/** One speaker and one speech bubble across setup, tours, and lessons. */
export function MascotMessage({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`mascot-message ${className}`}>
    <div className="mascot-message__sender">
      <img src="/mascot/portrait.png" alt="Git-It mascot" width={72} height={90} draggable={false} />
      <span aria-hidden="true">Git-It</span>
    </div>
    <div className="mascot-message__bubble">{children}</div>
  </div>
}
