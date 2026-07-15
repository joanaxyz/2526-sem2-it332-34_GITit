import type { CSSProperties, RefObject } from 'react'

import { ChallengeBattlePanel } from '@/features/challenges/components/ChallengeBattlePanel'
import {
  ChallengeDiagramStage,
  ChallengeSidebar,
  ChallengeTerminalStage,
  type ResizeStart,
  type WorkspaceFileInput,
} from '@/features/challenges/components/ChallengeWorkspacePanels'
import type { ChallengeRun } from '@/features/challenges/types'
import { ResizeHandle } from '@/shared/level/components/ResizeHandle'
import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
import type { TerminalPrompt } from '@/shared/level/terminalPrompt'
import type { TerminalLine } from '@/shared/level/types'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'

export function ChallengeWorkspaceMain({
  run,
  lines,
  shellPrompt,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  writeDisabled,
  workspaceGridRef,
  workspaceGridStyle,
  director,
  battleOpen,
  hasTargetDiagram,
  diagramGridRef,
  diagramGridStyle,
  terminalGridRef,
  terminalGridStyle,
  mutationPending,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
  onToggleBattle,
  onBeginDiagramResize,
  onBeginTerminalResize,
  onBeginTerminalPaneResize,
  onKeyboardDiagramResize,
  onKeyboardTerminalResize,
  onKeyboardTerminalPaneResize,
  onResetDiagramResize,
  onResetTerminalResize,
  onResetTerminalPaneResize,
  onCommand,
  onCloseEditor,
  onWriteFile,
}: {
  run: ChallengeRun
  lines: TerminalLine[]
  shellPrompt: TerminalPrompt
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  writeDisabled: boolean
  workspaceGridRef: RefObject<HTMLElement | null>
  workspaceGridStyle: CSSProperties
  director: BattleDirector
  battleOpen: boolean
  hasTargetDiagram: boolean
  diagramGridRef: RefObject<HTMLDivElement | null>
  diagramGridStyle: CSSProperties
  terminalGridRef: RefObject<HTMLDivElement | null>
  terminalGridStyle: CSSProperties
  mutationPending: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<ChallengeRun>
  onRenameFile: (input: { path: string; newPath: string }) => Promise<ChallengeRun>
  onDeleteFile: (path: string) => Promise<ChallengeRun>
  onOpenFile: (path: string | null) => void
  onToggleBattle: () => void
  onBeginDiagramResize: ResizeStart
  onBeginTerminalResize: ResizeStart
  onBeginTerminalPaneResize: ResizeStart
  onKeyboardDiagramResize: (delta: number) => void
  onKeyboardTerminalResize: (delta: number) => void
  onKeyboardTerminalPaneResize: (delta: number) => void
  onResetDiagramResize: () => void
  onResetTerminalResize: () => void
  onResetTerminalPaneResize: () => void
  onCommand: (command: string) => void
  onCloseEditor: () => void
  onWriteFile: (input: WorkspaceFileInput) => Promise<ChallengeRun>
}) {
  return (
    <main className="gameplay-workspace">
      <ChallengeSidebar
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
        ref={workspaceGridRef}
        className="gameplay-workspace__main"
        style={workspaceGridStyle}
      >
        <ChallengeBattlePanel
          run={run}
          director={director}
          open={battleOpen}
          onToggle={onToggleBattle}
          className="gameplay-battle-slot"
        />
        <ChallengeDiagramStage
          run={run}
          hasTargetDiagram={hasTargetDiagram}
          diagramGridRef={diagramGridRef}
          diagramGridStyle={diagramGridStyle}
          onBeginDiagramResize={onBeginDiagramResize}
          onKeyboardDiagramResize={onKeyboardDiagramResize}
          onResetDiagramResize={onResetDiagramResize}
        />
        <ResizeHandle
          label="Resize terminal height"
          orientation="horizontal"
          className="gameplay-resize gameplay-resize--horizontal"
          onPointerDown={onBeginTerminalResize}
          onKeyboardResize={onKeyboardTerminalResize}
          onReset={onResetTerminalResize}
        />
        <ChallengeTerminalStage
          run={run}
          lines={lines}
          prompt={shellPrompt}
          terminalGridRef={terminalGridRef}
          terminalGridStyle={terminalGridStyle}
          mutationPending={mutationPending}
          onBeginTerminalPaneResize={onBeginTerminalPaneResize}
          onKeyboardTerminalPaneResize={onKeyboardTerminalPaneResize}
          onResetTerminalPaneResize={onResetTerminalPaneResize}
          onCommand={onCommand}
        />
      </section>
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
