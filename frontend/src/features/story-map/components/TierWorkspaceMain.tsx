import { TierDiagramStage } from '@/features/story-map/components/tier-workspace/TierDiagramStage'
import { TierSidebar } from '@/features/story-map/components/tier-workspace/TierSidebar'
import { TierTerminalStage } from '@/features/story-map/components/tier-workspace/TierTerminalStage'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
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
  teachingActive,
  run,
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
  run: TierRun
  lines: TerminalLine[]
  shellPrompt: string
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  writeDisabled: boolean
  dagAnimation: TierDagAnimationController
  battleDirector: BattleDirector
  mutationPending: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<TierRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<TierRun>
  onDeleteFile: (path: string) => Promise<TierRun>
  onOpenFile: (path: string | null) => void
  onOpenStory: () => void
  onCommand: (command: string) => void
  onCloseEditor: () => void
  onWriteFile: (input: WorkspaceFileInput) => Promise<TierRun>
}) {
  return (
    <main className="gameplay-workspace tier-gameplay-workspace">
      <TierSidebar
        run={run}
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
        style={{ gridTemplateRows: `${WORKSPACE_BATTLE_STAGE_ROW} minmax(13rem, 1fr)` }}
      >
        <TierBattlePanel run={run} director={battleDirector} />
        <TierTerminalStage
          run={run}
          lines={lines}
          prompt={shellPrompt}
          mutationPending={mutationPending}
          dagAnimating={dagAnimation.animating}
          battleAnimating={battleDirector.animating}
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
