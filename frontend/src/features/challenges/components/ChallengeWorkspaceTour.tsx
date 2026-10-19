import { ScrollText, Star, TerminalSquare } from 'lucide-react'

import type { ChallengeRun } from '@/features/challenges/types'
import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { StarRulesContent } from '@/shared/level/components/StarRules'

const steps = [
  {
    id: 'challenge-story',
    selector: '[data-tour-target="challenge-brief"]',
    icon: ScrollText,
    title: 'Review the challenge',
    body: 'Read the scenario and objective. Required values are ready to copy into your commands.',
    placement: 'right',
  },
  {
    id: 'challenge-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: <StarRulesContent mode="challenge" />,
    placement: 'right',
  },
  {
    id: 'challenge-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows how many commands you have used and the most you can use. Finish before you run out. The Star target is your command goal for a higher score.',
    placement: 'right',
  },
  {
    id: 'challenge-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. Use project files and the repository diagrams to check your work. Your objective is checked automatically after each valid command; there is no Submit button.',
    placement: 'top',
  },
] satisfies readonly WorkspaceTourStep[]

export function ChallengeWorkspaceTour({ run, onClose }: {
  run: ChallengeRun
  onClose: () => void
}) {
  return (
    <GameplayWorkspaceTour
      label="Challenge quick tour"
      finishLabel="Start challenge"
      steps={steps}
      refreshKey={run.id}
      onClose={onClose}
    />
  )
}
