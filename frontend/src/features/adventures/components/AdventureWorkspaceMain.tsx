import type { CSSProperties } from 'react'

import { AdventureBattlePanel } from '@/features/adventures/components/AdventureBattlePanel'
import { AdventureContextPanel } from '@/features/adventures/components/AdventureContextPanel'
import type { AdventureAttempt, AdventureRun } from '@/features/adventures/types'
import { ProjectStructurePanel } from '@/shared/level/components/ProjectStructurePanel'
import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import { WorkspaceEditorOverlay } from '@/shared/level/components/WorkspaceEditorOverlay'
import { terminalPrompt } from '@/shared/level/terminalPrompt'
import type { TerminalLine } from '@/shared/level/types'
import type { BattleDirector } from '@/shared/battle/hooks/useBattleDirector'

type WorkspaceFileInput = { path: string; content: string }
type WorkspaceFileRenameInput = { path: string; newPath: string }

export function AdventureWorkspaceMain({
  run,
  workspaceRun,
  attempt,
  director,
  username,
  repoSlug,
  workspaceLines,
  workspaceGridStyle,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  writeDisabled,
  commandPending,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
  onCommand,
  onCloseEditor,
  onWriteFile,
}: {
  run: AdventureRun
  workspaceRun: AdventureRun
  attempt: AdventureAttempt
  director: BattleDirector
  username?: string
  repoSlug?: string
  workspaceLines: TerminalLine[]
  workspaceGridStyle: CSSProperties
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  writeDisabled: boolean
  commandPending: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<AdventureRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<AdventureRun>
  onDeleteFile: (path: string) => Promise<AdventureRun>
  onOpenFile: (path: string | null) => void
  onCommand: (command: string) => void
  onCloseEditor: () => void
  onWriteFile: (input: WorkspaceFileInput) => Promise<AdventureRun>
}) {
  return (
    <main className="gameplay-workspace">
      <aside
        className="gameplay-workspace__sidebar"
        style={{
          gridTemplateRows: projectFilesOpen
            ? 'minmax(13rem, 0.72fr) minmax(18rem, 0.58fr)'
            : 'minmax(13rem, 1fr) auto',
        }}
      >
        <div className="gameplay-panel-scroll app-scrollbar">
          <AdventureContextPanel run={workspaceRun} attempt={attempt} />
        </div>
        <div className="gameplay-project-region">
          <ProjectStructurePanel
            snapshot={attempt.repository_state}
            rootName={repoSlug}
            className="h-full"
            selectedPath={workspaceEditorPath}
            createDisabled={createDisabled}
            isOpen={projectFilesOpen}
            onToggle={onToggleProjectFiles}
            onCreateFile={onCreateFile}
            onRenameFile={onRenameFile}
            onDeleteFile={onDeleteFile}
            onOpenFile={onOpenFile}
          />
        </div>
      </aside>

      <section className="gameplay-workspace__main" style={workspaceGridStyle}>
        <AdventureBattlePanel
          run={workspaceRun}
          attempt={attempt}
          director={director}
          className="gameplay-battle-slot"
        />
        <div className="gameplay-terminal-grid">
          <div className="gameplay-pane" data-tour-target="terminal">
            <TerminalPanel
              lines={workspaceLines}
              prompt={terminalPrompt({
                username,
                host: run.story?.slug,
                repo: repoSlug,
              })}
              disabled={run.status !== 'started'}
              processing={commandPending}
              runDisabled={run.status !== 'started' || commandPending}
              className="h-full"
              onCommand={onCommand}
            />
          </div>
        </div>
      </section>
      <WorkspaceEditorOverlay
        snapshot={attempt.repository_state}
        filePath={workspaceEditorPath}
        open={Boolean(workspaceEditorPath)}
        writeDisabled={writeDisabled}
        onClose={onCloseEditor}
        onWriteFile={onWriteFile}
      />
    </main>
  )
}
