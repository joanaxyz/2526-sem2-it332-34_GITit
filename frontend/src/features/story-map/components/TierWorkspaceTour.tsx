import { ScrollText, Star, TerminalSquare } from 'lucide-react'

import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { StarRulesContent } from '@/shared/level/components/StarRules'

const steps = [
  {
    id: 'tier-story',
    selector: '[data-tour-target="tier-brief"]',
    icon: ScrollText,
    title: 'Review the objective',
    body: 'Read the objective and copy any required names or values. Use Story whenever you want to reread the setup.',
    placement: 'right',
  },
  {
    id: 'tier-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: <StarRulesContent mode="tier" />,
    placement: 'bottom',
  },
  {
    id: 'tier-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows how many commands you have used and the most you can use. Finish before you run out. The Star target is your command goal for a higher score.',
    placement: 'bottom',
  },
  {
    id: 'tier-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. Use project files and the repository diagrams to check your work. Your objective is checked automatically after each valid command; there is no Submit button.',
    placement: 'top',
  },
] satisfies readonly WorkspaceTourStep[]

const stepsWithDrawer = steps.map((step) => step.id === 'tier-terminal'
  ? { ...step, body: 'Type a command and press Enter. Use Repo graph to open the live diagram and compare it with the target graph. Your objective is checked automatically after each valid command; there is no Submit button.' }
  : step)

export function TierWorkspaceTour({ runId, onClose, targetInDrawer = false }: {
  runId: number
  onClose: () => void
  targetInDrawer?: boolean
}) {
  return (
    <GameplayWorkspaceTour
      label="Level quick tour"
      finishLabel="Start level"
      steps={targetInDrawer ? stepsWithDrawer : steps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
