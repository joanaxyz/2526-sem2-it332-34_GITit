import { useEffect, type Ref } from 'react'
import { ArrowRight, X } from 'lucide-react'
import type { MascotKnowledgeTip } from './mascotKnowledge'
import './knowledge-bubble.css'

export function MascotKnowledgeBubble({ id, tip, bubbleRef, onNext, onDismiss }: {
  id: string
  tip: MascotKnowledgeTip
  bubbleRef: Ref<HTMLDivElement>
  onNext: () => void
  onDismiss: (restoreFocus?: boolean) => void
}) {
  useEffect(() => {
    const outside = (event: PointerEvent) => {
      if (event.target instanceof Element && !event.target.closest('.world-mascot')) onDismiss()
    }
    const escape = (event: KeyboardEvent) => {
      if (event.key !== 'Escape' || event.defaultPrevented) return
      event.preventDefault()
      onDismiss(true)
    }
    document.addEventListener('pointerdown', outside)
    document.addEventListener('keydown', escape)
    return () => {
      document.removeEventListener('pointerdown', outside)
      document.removeEventListener('keydown', escape)
    }
  }, [onDismiss])

  return <div id={id} ref={bubbleRef} className="mascot-knowledge" role="region" aria-label="Git knowledge">
    <div className="mascot-knowledge__heading">
      <span>{tip.source}</span>
      <button type="button" aria-label="Dismiss tip" onClick={() => onDismiss(true)}><X size={16} aria-hidden="true" /></button>
    </div>
    <div role="status" aria-live="polite" aria-atomic="true">
      {tip.command ? <code className="mascot-knowledge__command">{tip.command}</code> : null}
      <p>{tip.text}</p>
    </div>
    <button type="button" className="mascot-knowledge__next" onClick={onNext}>Another tip <ArrowRight size={14} aria-hidden="true" /></button>
  </div>
}
