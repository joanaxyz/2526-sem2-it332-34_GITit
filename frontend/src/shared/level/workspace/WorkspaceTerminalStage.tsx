import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { useTerminalLocation } from '@/shared/level-runtime/terminalCwd'
import { repositoryFolderName } from '@/shared/level/utils/gitDirectory'
import type { TerminalLine } from '@/shared/level/types'
import type { WorkspaceRun, WorkspaceScene } from '@/shared/level/workspace/types'

/** Full-width terminal under the battle stage, with the prompt following its output. */
export function WorkspaceTerminalStage({
  run,
  scene,
  lines,
  prompt,
  mutationPending,
  dagAnimating,
  battleAnimating,
  onCommand,
}: {
  run: WorkspaceRun
  scene: Pick<WorkspaceScene, 'runQueryKey' | 'rootName'>
  lines: TerminalLine[]
  prompt: string
  mutationPending: boolean
  dagAnimating: boolean
  battleAnimating: boolean
  onCommand: (command: string) => void
}) {
  const location = useTerminalLocation(scene.runQueryKey, run.repository_state)
  // Like `pwd` without `/workspace/`: the project folder (named by `git init
  // <dir>` / `git clone` once there is one), then the folder inside it.
  const folder = repositoryFolderName(run.repository_state, scene.rootName || 'project')
  const locationLabel = location.outside ? 'workspace' : [folder, location.cwd].filter(Boolean).join('/')
  return (
    <div className="gameplay-terminal-grid tier-terminal-stage" data-testid="tier-terminal-stage">
      <div className="gameplay-pane" data-tour-target="terminal">
        <TerminalPanel
          lines={lines}
          prompt={prompt}
          location={locationLabel}
          disabled={run.status !== 'started'}
          runDisabled={mutationPending || dagAnimating || battleAnimating}
          processing={mutationPending}
          className="h-full"
          onCommand={onCommand}
        />
      </div>
    </div>
  )
}
