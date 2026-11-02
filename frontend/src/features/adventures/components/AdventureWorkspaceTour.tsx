import { ScrollText, TerminalSquare, CircleCheck } from 'lucide-react'

import {
  GameplayWorkspaceTour,
  type WorkspaceTourStep,
} from '@/shared/level/components/GameplayWorkspaceTour'

const adventureWorkspaceTourSteps = [
  {
    id: 'adventure-story',
    selector: '[data-tour-target="adventure-story"]',
    icon: ScrollText,
    title: 'Read the objective first',
    body: 'The task and live checklist tell you exactly what Git commands to run. New checks tick automatically as you work.',
    placement: 'right',
  },
  {
    id: 'adventure-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Type a Git command',
    body: 'Type a command and press Enter. Each result is checked immediately — no separate Submit button.',
    placement: 'top',
  },
  {
    id: 'adventure-completion',
    selector: '[data-tour-target="star-budget"]',
    icon: CircleCheck,
    title: 'Finish within the limit',
    body: 'Complete all waves to earn stars. The command counter shows used / limit for this wave — keep an eye on it.',
    placement: 'right',
  },
] satisfies readonly WorkspaceTourStep[]

export function AdventureWorkspaceTour({
  runId,
  onClose,
}: {
  runId: number
  onClose: () => void
}) {
  return (
    <GameplayWorkspaceTour
      label="Adventure quick tour"
      finishLabel="Start"
      steps={adventureWorkspaceTourSteps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
