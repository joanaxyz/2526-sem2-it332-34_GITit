import { useEffect, useRef } from 'react'

import { FloatingMascotLauncher } from '@/shared/mascot/FloatingMascotLauncher'

/** What a finished run offers next: the next scenario, difficulty or trial, a retry, or the map. */
export type OutcomeNextStep = {
  /** The short tag under the portrait, e.g. "Continue". */
  caption: string
  /** The speech bubble's invitation, e.g. "Click me to continue to the next scenario!" */
  prompt: string
  /** An optional second line, e.g. the next scenario's title. */
  detail?: string
  /** Set while the step is already under way; the bubble then shows `pendingPrompt`. */
  pending?: boolean
  pendingPrompt?: string
  onSelect: () => void
}

// The workspace mascots a finished run's Git-It takes over from: the command
// guide launcher and, when a tutorial card was open, its "Ask Git-It" launcher.
const WORKSPACE_LAUNCHERS = ['command-guide', 'guide-tutor'] as const

/**
 * Once the outcome modal is dismissed, Git-It stays in the workspace with a
 * speech bubble; clicking either moves on to the run's next step, so the
 * learner never has to go back to the map to keep playing. It is the same
 * mascot repurposed: it stands where the workspace's mascot last stood.
 */
export function OutcomeNextStepMascot({ step }: { step: OutcomeNextStep }) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const prompt = step.pending ? step.pendingPrompt ?? 'One moment…' : step.prompt
  const select = () => {
    if (!step.pending) step.onSelect()
  }

  // The modal it replaces held focus; hand it to the mascot so Enter moves on.
  useEffect(() => {
    buttonRef.current?.focus({ preventScroll: true })
  }, [])

  return (
    <FloatingMascotLauncher
      name="outcome-next-step"
      label={step.detail ? `${prompt} ${step.detail}` : prompt}
      caption={step.caption}
      size="large"
      takeOverFrom={WORKSPACE_LAUNCHERS}
      buttonRef={buttonRef}
      onOpen={select}
    >
      <div className="outcome-next-step" aria-hidden="true" data-pending={step.pending || undefined} onClick={select}>
        <strong className="outcome-next-step__prompt">{prompt}</strong>
        {step.detail ? <span className="outcome-next-step__detail">{step.detail}</span> : null}
      </div>
    </FloatingMascotLauncher>
  )
}
