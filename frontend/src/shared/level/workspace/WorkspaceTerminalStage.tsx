import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { useTerminalCwd } from '@/shared/level-runtime/terminalCwd'
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
  scene: Pick<WorkspaceScene, 'runQueryKey'>
  lines: TerminalLine[]
  prompt: string
  mutationPending: boolean
  dagAnimating: boolean
  battleAnimating: boolean
  onCommand: (command: string) => void
}) {
  const cwd = useTerminalCwd(scene.runQueryKey, run.repository_state)
  return (
    <div className="gameplay-terminal-grid tier-terminal-stage" data-testid="tier-terminal-stage">
      <div className="gameplay-pane" data-tour-target="terminal">
        <TerminalPanel
          lines={lines}
          prompt={prompt}
          cwd={cwd}
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
