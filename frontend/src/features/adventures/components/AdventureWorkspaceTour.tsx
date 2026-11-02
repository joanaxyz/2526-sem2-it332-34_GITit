import { BookOpen, CircleCheck, FolderTree, ScrollText, Star, Swords, TerminalSquare } from 'lucide-react'

import {
  GameplayWorkspaceTour,
  type WorkspaceTourStep,
} from '@/shared/level/components/GameplayWorkspaceTour'

const adventureWorkspaceTourSteps = [
  {
    id: 'adventure-story',
    selector: '[data-tour-target="adventure-story"]',
    icon: ScrollText,
    title: 'Review the objective',
    body: 'Read the task and live checks first. They describe the current wave, including any required Git commands.',
    placement: 'right',
  },
  {
    id: 'adventure-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: 'Clear every wave for 1 star. Meet each wave\'s Star target for 2; do both on your first try for 3. Your lowest wave score sets the level score.',
    placement: 'right',
  },
  {
    id: 'adventure-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows used / limit for this wave. Changes and invalid commands count; valid read-only inspections are free. Solve by the last counted command or the run ends. Each wave resets the count.',
    placement: 'right',
  },
  {
    id: 'adventure-guide',
    selector: '[data-tour-target="level-guide"]',
    icon: BookOpen,
    title: 'The guide costs a star',
    body: 'Opening the command guide subtracts one star from a completed run, with a minimum of 1. The penalty applies only once, even if you reopen it.',
    placement: 'bottom',
  },
  {
    id: 'adventure-battle',
    selector: '[data-testid="battle-stage"]',
    icon: Swords,
    title: 'See command results',
    body: 'Valid repository changes become battle actions, so the result reflects the state you create.',
    placement: 'bottom',
  },
  {
    id: 'adventure-project',
    selector: '[data-tour-target="project-files"]',
    icon: FolderTree,
    title: 'Check project files',
    body: 'Open or edit files when the objective depends on their contents. This tree reflects the current workspace.',
    placement: 'right',
  },
  {
    id: 'adventure-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. You can copy required values and use Paste here without running them automatically.',
    placement: 'top',
  },
  {
    id: 'adventure-completion',
    selector: '[data-tour-target="adventure-story"]',
    icon: CircleCheck,
    title: 'Complete every wave',
    body: 'After each valid command, your work is checked automatically. Satisfy the current wave to advance; clear every wave to finish the level and earn stars. No separate Submit button.',
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
      finishLabel="Start adventure"
      steps={adventureWorkspaceTourSteps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
