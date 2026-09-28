import { ChevronRight } from 'lucide-react'

import type { OrientationStep } from '@/features/story-map/components/orientation/types'
import { Button } from '@/shared/components/Button'
import { CopyButton } from '@/shared/components/CopyButton'

export function OrientationStepAction({
  onClick,
  children = 'Complete & continue',
  disabled = false,
}: {
  onClick: () => void
  children?: string
  disabled?: boolean
}) {
  return (
    <Button type="button" className="orientation-step-primary-action" disabled={disabled} onClick={onClick}>
      {children} <ChevronRight aria-hidden="true" />
    </Button>
  )
}

export function OrientationCommandLesson({
  step,
  hasNextStep,
  onContinue,
}: {
  step: OrientationStep
  hasNextStep: boolean
  onContinue: () => void
}) {
  const command = (step.accept_prefixes ?? step.accept_exact ?? [])[0] ?? step.hint ?? 'See the prompt above.'

  return (
    <div className="orientation-command-lesson">
      <div className="orientation-command-block">
        <div className="orientation-command-label">
          <span>{step.kind === 'git_command' ? 'Git command' : 'Shell command'}</span>
          <CopyButton value={command} label="command" />
        </div>
        <pre><code>{command}</code></pre>
      </div>
      {step.success_output ? (
        <div className="orientation-output-block">
          <span>Expected output</span>
          <pre><code>{step.success_output}</code></pre>
        </div>
      ) : null}
      {step.hint ? <p className="orientation-hint">{step.hint}</p> : null}
      <OrientationStepAction onClick={onContinue}>
        {hasNextStep ? 'I tried this — continue' : 'Mark step complete'}
      </OrientationStepAction>
    </div>
  )
}
