import type { CSSProperties, PointerEvent, RefObject } from 'react'

import { TierContextualFeedbackPanel } from '@/features/story-map/components/TierContextualFeedbackPanel'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { ResizeHandle } from '@/shared/level/components/ResizeHandle'
import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { queryKeys } from '@/shared/api/queryKeys'
import { useTerminalCwd } from '@/shared/level-runtime/terminalCwd'
import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

export type ResizeStart = (event: PointerEvent<HTMLElement>) => void

export function TierTerminalStage({
  teachingActive = false,
  run,
  lines,
  prompt,
  terminalGridRef,
  terminalGridStyle,
  mutationPending,
  dagAnimating,
  battleAnimating,
  onBeginTerminalPaneResize,
  onKeyboardTerminalPaneResize,
  onResetTerminalPaneResize,
  onCommand,
}: {
  teachingActive?: boolean
  run: TierRun
  lines: TerminalLine[]
  prompt: string
  terminalGridRef: RefObject<HTMLDivElement | null>
  terminalGridStyle: CSSProperties
  mutationPending: boolean
  dagAnimating: boolean
  battleAnimating: boolean
  onBeginTerminalPaneResize: ResizeStart
  onKeyboardTerminalPaneResize: (delta: number) => void
  onResetTerminalPaneResize: () => void
  onCommand: (command: string) => void
}) {
  const cwd = useTerminalCwd(queryKeys.adventureTierRun(run.id), run.repository_state)
  return (
    <div
      ref={terminalGridRef}
      data-testid="terminal-feedback-grid"
      className={cn(
        'gameplay-terminal-grid',
        (!teachingActive && run.scaffolding.contextual_feedback) && 'has-feedback',
      )}
      style={terminalGridStyle}
    >
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
      {!teachingActive && run.scaffolding.contextual_feedback ? (
        <ResizeHandle
          label="Resize terminal and feedback"
          orientation="vertical"
          className="gameplay-resize gameplay-resize--vertical"
          onPointerDown={onBeginTerminalPaneResize}
          onKeyboardResize={onKeyboardTerminalPaneResize}
          onReset={onResetTerminalPaneResize}
        />
      ) : null}
      {!teachingActive && run.scaffolding.contextual_feedback ? (
        <div className="gameplay-pane" data-tour-target="feedback">
          <TierContextualFeedbackPanel run={run} />
        </div>
      ) : null}
    </div>
  )
}
