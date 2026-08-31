import { BookOpen, FolderTree, ScrollText, Star, Swords, TerminalSquare } from 'lucide-react'

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
    body: 'Read the task and live checks first. The level finishes on its own once every check is satisfied.',
    placement: 'right',
  },
  {
    id: 'adventure-scoring',
    selector: '[data-tour-target="adventure-story"]',
    icon: Star,
    title: 'Earn up to 3 stars',
    body: 'Finishing earns 1 star, staying within the command budget earns 2, and a first-try clear earns all 3 — tracked live in the Stars row.',
    placement: 'right',
  },
  {
    id: 'adventure-guide',
    selector: '[data-tour-target="level-guide"]',
    icon: BookOpen,
    title: 'The guide costs a star',
    body: 'Stuck? Open the command guide for reference — it costs this run one star, never dropping below 1.',
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
