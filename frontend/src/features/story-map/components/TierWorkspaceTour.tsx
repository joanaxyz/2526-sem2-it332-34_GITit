import { FolderTree, GitBranch, ScrollText, Star, TerminalSquare } from 'lucide-react'

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
    id: 'tier-diagram',
    selector: '[data-tour-target="live-dag"]',
    icon: GitBranch,
    title: 'Read the repository diagrams',
    body: 'The live diagram shows your commits, branches, and HEAD. If a target diagram is shown, compare its repository shape with the live one as you work.',
    placement: 'bottom',
  },
  {
    id: 'tier-project',
    selector: '[data-tour-target="project-files"]',
    icon: FolderTree,
    title: 'Browse project files',
    body: 'Open files here to inspect or edit them when the objective depends on their contents. Save edits, then use Git commands if the task asks you to stage or commit.',
    placement: 'right',
  },
  {
    id: 'tier-terminal',
    selector: '[data-command-input]',
    icon: TerminalSquare,
    title: 'Run a Git command',
    body: 'Type a command and press Enter. Your objective is checked automatically after each valid command; there is no Submit button.',
    placement: 'top',
  },
] satisfies readonly WorkspaceTourStep[]

const stepsWithDrawer = steps.map((step) => step.id === 'tier-diagram'
  ? { ...step, body: 'Open Repo graph to see the live commits, branches, and HEAD. If a target diagram is shown, compare its repository shape with the live one as you work.' }
  : step)

export function TierWorkspaceTour({ runId, onClose, repoGraphInDrawer = false }: {
  runId: number
  onClose: () => void
  repoGraphInDrawer?: boolean
}) {
  return (
    <GameplayWorkspaceTour
      label="Level quick tour"
      finishLabel="Start level"
      steps={repoGraphInDrawer ? stepsWithDrawer : steps}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
