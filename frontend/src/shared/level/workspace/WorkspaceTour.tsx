import { FolderTree, GitBranch, ScrollText, Star, TerminalSquare } from 'lucide-react'

import { GameplayWorkspaceTour, type WorkspaceTourStep } from '@/shared/level/components/GameplayWorkspaceTour'
import { StarRulesContent } from '@/shared/level/components/StarRules'

type WorkspaceTourMode = 'tier' | 'challenge'

const COPY: Record<WorkspaceTourMode, { label: string; finishLabel: string }> = {
  tier: { label: 'Level quick tour', finishLabel: 'Start level' },
  challenge: { label: 'Challenge quick tour', finishLabel: 'Start challenge' },
}

function tourSteps(mode: WorkspaceTourMode, repoGraphInDrawer: boolean) {
  return [
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
      body: <StarRulesContent mode={mode} />,
      placement: 'bottom',
    },
    {
      id: 'tier-budget',
      selector: '[data-tour-target="command-budget"]',
      icon: TerminalSquare,
      title: 'Watch the command limit',
      body: 'Commands shows how many commands you have used and the most you can use. Finish on or before the last allowed command. Select the stars to view scoring targets and rules. Retries never reduce stars.',
      placement: 'bottom',
    },
    {
      id: 'tier-diagram',
      selector: '[data-tour-target="live-dag"]',
      icon: GitBranch,
      title: 'Read the repository diagrams',
      body: repoGraphInDrawer
        ? 'Open Repo graph to see the live commits, branches, and HEAD. If a target diagram is shown, compare its repository shape with the live one as you work.'
        : 'The live diagram shows your commits, branches, and HEAD. If a target diagram is shown, compare its repository shape with the live one as you work.',
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
}

/** First-run tour of the gameplay workspace, for adventure tiers and Challenge Gate trials. */
export function WorkspaceTour({ mode = 'tier', runId, onClose, repoGraphInDrawer = false }: {
  mode?: WorkspaceTourMode
  runId: number
  onClose: () => void
  repoGraphInDrawer?: boolean
}) {
  return (
    <GameplayWorkspaceTour
      label={COPY[mode].label}
      finishLabel={COPY[mode].finishLabel}
      steps={tourSteps(mode, repoGraphInDrawer)}
      refreshKey={runId}
      onClose={onClose}
    />
  )
}
