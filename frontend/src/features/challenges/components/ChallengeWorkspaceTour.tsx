import { GitBranch, MessageSquareText, ScrollText, Star, Target, TerminalSquare } from 'lucide-react'

import type { ChallengeRun } from '@/features/challenges/types'
import {
  GameplayWorkspaceTour,
  type WorkspaceTourStep,
} from '@/shared/level/components/GameplayWorkspaceTour'

const challengeWorkspaceTourSteps = [
  {
    id: 'challenge-story',
    selector: '[data-tour-target="challenge-brief"]',
    icon: ScrollText,
    title: 'Review the challenge',
    body: 'Scenario explains the setup. Objective states the required result, and Required values are ready to copy. It finishes on its own once the repository matches.',
    placement: 'right',
  },
  {
    id: 'challenge-scoring',
    selector: '[data-tour-target="challenge-brief"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: 'Solving earns 1 star, staying within the command budget earns 2, and a first-try clear earns all 3 — tracked live in the Stars row.',
    placement: 'right',
  },
  {
    id: 'challenge-live-dag',
    selector: '[data-tour-target="live-dag"]',
    icon: GitBranch,
    title: 'Track repository state',
    body: 'The live DAG shows the current commits, branches, and HEAD after every valid command.',
    placement: 'bottom',
  },
  {
    id: 'challenge-target-dag',
    selector: '[data-tour-target="expected-state"]',
    icon: Target,
    title: 'Compare the target',
    body: 'When available, the target DAG shows the repository shape to reach without revealing the command sequence.',
    placement: 'bottom',
    optional: true,
  },
  {
    id: 'challenge-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Copy a required value or use Paste in the terminal, then press Enter. Inspecting is free; changes use the action budget.',
    placement: 'top',
  },
  {
    id: 'challenge-feedback',
    selector: '[data-tour-target="feedback"]',
    icon: MessageSquareText,
    title: 'Use the feedback',
    body: 'After a command, this panel explains what changed so you can adjust without being given the solution.',
    placement: 'top',
    optional: true,
  },
] satisfies readonly WorkspaceTourStep[]

export function ChallengeWorkspaceTour({
  run,
  onClose,
}: {
  run: ChallengeRun
  onClose: () => void
}) {
  return (
    <GameplayWorkspaceTour
      label="Challenge quick tour"
      finishLabel="Start challenge"
      steps={challengeWorkspaceTourSteps}
      refreshKey={run.id}
      onClose={onClose}
    />
  )
}
