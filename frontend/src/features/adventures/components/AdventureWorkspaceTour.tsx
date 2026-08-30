import { FolderTree, ScrollText, Swords, TerminalSquare } from 'lucide-react'

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
    body: 'Read the task and live checks first. They describe the repository state this level expects.',
    placement: 'right',
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
