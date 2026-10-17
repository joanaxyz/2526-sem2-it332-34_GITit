import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { queryKeys } from '@/shared/api/queryKeys'
import { useTerminalCwd } from '@/shared/level-runtime/terminalCwd'
import type { TerminalLine } from '@/shared/level/types'

/** Full-width terminal under the battle stage, input docked at its foot; contextual feedback lives in the sidebar. */
export function TierTerminalStage({
  run,
  lines,
  prompt,
  mutationPending,
  dagAnimating,
  battleAnimating,
  onCommand,
}: {
  run: TierRun
  lines: TerminalLine[]
  prompt: string
  mutationPending: boolean
  dagAnimating: boolean
  battleAnimating: boolean
  onCommand: (command: string) => void
}) {
  const cwd = useTerminalCwd(queryKeys.adventureTierRun(run.id), run.repository_state)
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
          dockInput
          onCommand={onCommand}
        />
      </div>
    </div>
  )
}
