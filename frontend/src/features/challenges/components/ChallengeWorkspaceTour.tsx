import { CircleCheck, FolderTree, GitBranch, MessageSquareText, ScrollText, Star, Target, TerminalSquare } from 'lucide-react'

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
    body: 'Scenario explains the setup. Objective states the required result, and Required values are ready to copy.',
    placement: 'right',
  },
  {
    id: 'challenge-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: 'Solve for 1 star. Use no more counted commands than the Star target for 2. Solve within that target on your first try for 3. Stars are awarded when you finish.',
    placement: 'right',
  },
  {
    id: 'challenge-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows used / limit. Changes and invalid commands count; valid read-only inspections are free. Solve by the last counted command or the run ends. The Star target is a separate scoring goal.',
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
    id: 'challenge-project',
    selector: '[data-tour-target="project-files"]',
    icon: FolderTree,
    title: 'Check project files',
    body: 'Open or edit files here when the objective requires specific contents. Save edits, then use Git to stage or commit them if the task requires it.',
    placement: 'right',
    optional: true,
  },
  {
    id: 'challenge-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. You can copy required values and use Paste here without running them automatically.',
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
  {
    id: 'challenge-completion',
    selector: '[data-tour-target="challenge-brief"]',
    icon: CircleCheck,
    title: 'Complete the objective',
    body: 'After each valid command, all objective requirements are checked, including file contents and required commands. Complete them to see your results; no separate Submit button.',
    placement: 'right',
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
