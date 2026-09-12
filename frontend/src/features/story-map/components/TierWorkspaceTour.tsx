import { CircleCheck, FolderTree, GitBranch, MessageSquareText, ScrollText, Star, Swords, Target, TerminalSquare } from 'lucide-react'

import {
  GameplayWorkspaceTour,
  type WorkspaceTourStep,
} from '@/shared/level/components/GameplayWorkspaceTour'

/* The tier workspace is how every difficulty-tiered adventure level is played,
   so it needs its own first-run tour: the plain adventure tour describes waves
   and a command guide this screen does not have, and the challenge tour is
   Challenge Gate copy. Steps that depend on the tier's scaffolding are
   optional - GameplayWorkspaceTour drops the whole tour when a required
   target is missing. */
const tierWorkspaceTourSteps = [
  {
    id: 'tier-story',
    selector: '[data-tour-target="tier-brief"]',
    icon: ScrollText,
    title: 'Review the objective',
    body: 'Scenario sets up the repository you were handed. Objective states the result you have to reach at this difficulty.',
    placement: 'right',
  },
  {
    id: 'tier-scoring',
    selector: '[data-tour-target="star-budget"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: 'Solve the level for 1 star. Use no more counted commands than the Star target for 2. Do both on your first try for 3.',
    placement: 'right',
  },
  {
    id: 'tier-budget',
    selector: '[data-tour-target="command-budget"]',
    icon: TerminalSquare,
    title: 'Watch the command limit',
    body: 'Commands shows used / limit. Changes and invalid commands count; valid read-only inspections are free. Solve by the last counted command or the run ends.',
    placement: 'right',
  },
  {
    id: 'tier-battle',
    selector: '[data-testid="battle-stage"]',
    icon: Swords,
    title: 'See command results',
    body: 'Valid repository changes become battle actions, so what happens on stage reflects the state you create.',
    placement: 'bottom',
  },
  {
    id: 'tier-live-dag',
    selector: '[data-tour-target="live-dag"]',
    icon: GitBranch,
    title: 'Track repository state',
    body: 'The live diagram shows the current commits, branches, and HEAD after every valid command.',
    placement: 'bottom',
  },
  {
    id: 'tier-target-dag',
    selector: '[data-tour-target="expected-state"]',
    icon: Target,
    title: 'Compare the target',
    body: 'When available, the target diagram shows the repository shape to reach without revealing the command sequence.',
    placement: 'bottom',
    optional: true,
  },
  {
    id: 'tier-project',
    selector: '[data-tour-target="project-files"]',
    icon: FolderTree,
    title: 'Check project files',
    body: 'Open or edit files here when the objective depends on their contents. Save edits, then use Git to stage or commit them if the task requires it.',
    placement: 'right',
  },
  {
    id: 'tier-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. You can copy required values and use Paste here without running them automatically.',
    placement: 'top',
  },
  {
    id: 'tier-feedback',
    selector: '[data-tour-target="feedback"]',
    icon: MessageSquareText,
    title: 'Use the feedback',
    body: 'After a command, this panel explains what changed so you can adjust without being given the solution.',
    placement: 'top',
    optional: true,
  },
  {
    id: 'tier-completion',
    selector: '[data-tour-target="tier-brief"]',
    icon: CircleCheck,
    title: 'Complete the objective',
    body: 'Your work is checked after each valid command, so there is no Submit button. Meet the objective to finish the run and earn stars, then move up a difficulty.',
    placement: 'right',
  },
] satisfies readonly WorkspaceTourStep[]

export function TierWorkspaceTour({ runId, onClose }: { runId: number; onClose: () => void }) {
  return (
    <GameplayWorkspaceTour
      label="Level quick tour"
      finishLabel="Start level"
      steps={tierWorkspaceTourSteps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
