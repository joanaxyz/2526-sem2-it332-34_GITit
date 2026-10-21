import type { CSSProperties } from 'react'

import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
import type { TerminalLine } from '@/shared/level/types'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'
import { WORKSPACE_BATTLE_STAGE_ROW } from '@/shared/level/workspaceLayout'
import { WorkspaceBattlePanel } from '@/shared/level/workspace/WorkspaceBattlePanel'
import { WorkspaceDiagramStage } from '@/shared/level/workspace/WorkspaceDiagramStage'
import { WorkspaceSidebar } from '@/shared/level/workspace/WorkspaceSidebar'
import { WorkspaceTerminalStage } from '@/shared/level/workspace/WorkspaceTerminalStage'
import type { RepoGraphDrawer, WorkspaceRun, WorkspaceScene } from '@/shared/level/workspace/types'
import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'

/**
 * The gameplay workspace shared by adventure tiers and Challenge Gate trials:
 * objectives and files on the left, the battle stage over the terminal in the
 * middle, and the Live/Expected diagrams on the right.
 */
export function GameplayWorkspaceMain({
  teachingActive,
  repoGraphDrawer,
  run,
  scene,
  lines,
  shellPrompt,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  writeDisabled,
  dagAnimation,
  battleDirector,
  mutationPending,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
  onOpenStory,
  onCommand,
  onCloseEditor,
  onWriteFile,
}: {
  teachingActive?: boolean
  /** Present while the layout shows the repository graph as a drawer. */
  repoGraphDrawer?: RepoGraphDrawer
  run: WorkspaceRun
  scene: WorkspaceScene
  lines: TerminalLine[]
  shellPrompt: string
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  writeDisabled: boolean
  dagAnimation: DagAnimationController
  battleDirector: BattleDirector
  mutationPending: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<unknown>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<unknown>
  onDeleteFile: (path: string) => Promise<unknown>
  onOpenFile: (path: string | null) => void
  onOpenStory: () => void
  onCommand: (command: string) => void
  onCloseEditor: () => void
  onWriteFile: (input: WorkspaceFileInput) => Promise<unknown>
}) {
  return (
    <main className="gameplay-workspace tier-gameplay-workspace">
      <WorkspaceSidebar
        run={run}
        scene={scene}
        teachingActive={teachingActive}
        projectFilesOpen={projectFilesOpen}
        workspaceEditorPath={workspaceEditorPath}
        createDisabled={createDisabled}
        onToggleProjectFiles={onToggleProjectFiles}
        onCreateFile={onCreateFile}
        onRenameFile={onRenameFile}
        onDeleteFile={onDeleteFile}
        onOpenFile={onOpenFile}
        onOpenStory={onOpenStory}
      />
      <section
        className="gameplay-workspace__main challenge-workspace__main tier-workspace__main"
        style={{ '--tier-battle-row': WORKSPACE_BATTLE_STAGE_ROW } as CSSProperties}
      >
        <WorkspaceBattlePanel run={run} scene={scene} director={battleDirector} />
        <WorkspaceTerminalStage
          run={run}
          scene={scene}
          lines={lines}
          prompt={shellPrompt}
          mutationPending={mutationPending}
          dagAnimating={dagAnimation.animating}
          battleAnimating={battleDirector.animating}
          onCommand={onCommand}
        />
      </section>
      <WorkspaceDiagramStage
        run={run}
        animation={dagAnimation}
        drawer={repoGraphDrawer}
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
