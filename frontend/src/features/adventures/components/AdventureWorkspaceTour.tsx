import { FolderTree, ScrollText, Star, Swords, TerminalSquare } from 'lucide-react'

import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { StarRulesContent } from '@/shared/level/components/StarRules'

const steps = [
  {
    id: 'adventure-story',
    selector: '[data-tour-target="adventure-story"]',
    icon: ScrollText,
    title: 'Review the objective',
    body: 'Read the task for this wave. Complete its checks to move on; clear every wave to finish the level.',
    placement: 'right',
  },
  {
    id: 'adventure-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: <StarRulesContent mode="adventure" />,
    placement: 'right',
  },
  {
    id: 'adventure-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows how many commands you have used and the most you can use. Finish before you run out. The Star target is your command goal for a higher score. Each wave starts a new command count.',
    placement: 'right',
  },
  {
    id: 'adventure-battle',
    selector: '[data-testid="battle-stage"]',
    icon: Swords,
    title: 'See command results',
    body: 'Valid repository changes play out on this stage, so the battle reflects the state you create.',
    placement: 'bottom',
  },
  {
    id: 'adventure-project',
    selector: '[data-tour-target="project-files"]',
    icon: FolderTree,
    title: 'Browse project files',
    body: 'Open files here to inspect or edit them when the task depends on their contents. This tree shows the current workspace.',
    placement: 'right',
  },
  {
    id: 'adventure-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. Your objective is checked automatically after each valid command; there is no Submit button.',
    placement: 'top',
  },
] satisfies readonly WorkspaceTourStep[]

export function AdventureWorkspaceTour({ runId, onClose }: {
  runId: number
  onClose: () => void
}) {
  return (
    <GameplayWorkspaceTour
      label="Adventure quick tour"
      finishLabel="Start adventure"
      steps={steps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
