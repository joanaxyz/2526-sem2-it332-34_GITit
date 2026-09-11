import type { CSSProperties, RefObject } from 'react'

import {
  TierDiagramStage,
  TierSidebar,
  TierTerminalStage,
  type ResizeStart,
} from '@/features/story-map/components/TierWorkspacePanels'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
import type { TerminalPrompt } from '@/shared/level/terminalPrompt'
import type { TerminalLine } from '@/shared/level/types'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import { TierBattlePanel } from '@/features/story-map/components/TierBattlePanel'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { WORKSPACE_BATTLE_STAGE_ROW } from '@/shared/level/workspaceLayout'

export function TierWorkspaceMain({
  run,
  lines,
  shellPrompt,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  writeDisabled,
  dagAnimation,
  battleDirector,
  terminalGridRef,
  terminalGridStyle,
  mutationPending,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
  onBeginTerminalPaneResize,
  onKeyboardTerminalPaneResize,
  onResetTerminalPaneResize,
  onCommand,
  onCloseEditor,
  onWriteFile,
}: {
  run: TierRun
  lines: TerminalLine[]
  shellPrompt: TerminalPrompt
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  writeDisabled: boolean
  dagAnimation: TierDagAnimationController
  battleDirector: BattleDirector
  terminalGridRef: RefObject<HTMLDivElement | null>
  terminalGridStyle: CSSProperties
  mutationPending: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<TierRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<TierRun>
  onDeleteFile: (path: string) => Promise<TierRun>
  onOpenFile: (path: string | null) => void
  onBeginTerminalPaneResize: ResizeStart
  onKeyboardTerminalPaneResize: (delta: number) => void
  onResetTerminalPaneResize: () => void
  onCommand: (command: string) => void
  onCloseEditor: () => void
  onWriteFile: (input: WorkspaceFileInput) => Promise<TierRun>
}) {
  return (
    <main className="gameplay-workspace tier-gameplay-workspace">
      <TierSidebar
        run={run}
        projectFilesOpen={projectFilesOpen}
        workspaceEditorPath={workspaceEditorPath}
        createDisabled={createDisabled}
        onToggleProjectFiles={onToggleProjectFiles}
        onCreateFile={onCreateFile}
        onRenameFile={onRenameFile}
        onDeleteFile={onDeleteFile}
        onOpenFile={onOpenFile}
      />
      <section
        className="gameplay-workspace__main challenge-workspace__main tier-workspace__main"
        style={{ gridTemplateRows: `${WORKSPACE_BATTLE_STAGE_ROW} minmax(13rem, 1fr)` }}
      >
        <TierBattlePanel run={run} director={battleDirector} />
        <TierTerminalStage
          run={run}
          lines={lines}
          prompt={shellPrompt}
          terminalGridRef={terminalGridRef}
          terminalGridStyle={terminalGridStyle}
          mutationPending={mutationPending}
          dagAnimating={dagAnimation.animating}
          battleAnimating={battleDirector.animating}
          onBeginTerminalPaneResize={onBeginTerminalPaneResize}
          onKeyboardTerminalPaneResize={onKeyboardTerminalPaneResize}
          onResetTerminalPaneResize={onResetTerminalPaneResize}
          onCommand={onCommand}
        />
      </section>
      <TierDiagramStage
        run={run}
        animation={dagAnimation}
      />
      <WorkspaceEditorOverlay
        snapshot={run.repository_state}
        filePath={workspaceEditorPath}
        open={Boolean(workspaceEditorPath)}
        writeDisabled={writeDisabled}
        onClose={onCloseEditor}
        onWriteFile={onWriteFile}
      />
    </main>
  )
}
