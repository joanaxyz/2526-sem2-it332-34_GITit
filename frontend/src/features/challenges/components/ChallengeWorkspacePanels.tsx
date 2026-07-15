import type { CSSProperties, PointerEvent, RefObject } from 'react'

import { ChallengeContextPanel } from '@/features/challenges/components/ChallengeContextPanel'
import { ChallengeDagLegend } from '@/features/challenges/components/ChallengeDagLegend'
import { ContextualFeedbackPanel } from '@/features/challenges/components/ContextualFeedbackPanel'
import { DAG_ZOOM_KEY } from '@/features/challenges/components/challengeWorkspaceLayout'
import type { ChallengeRun } from '@/features/challenges/types'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import { ProjectStructurePanel } from '@/shared/level/components/ProjectStructurePanel'
import { ResizeHandle } from '@/shared/level/components/ResizeHandle'
import { TerminalPanel } from '@/shared/level/components/TerminalPanel'
import type { TerminalPrompt } from '@/shared/level/terminalPrompt'
import type { TerminalLine } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

export type WorkspaceFileInput = { path: string; content: string }
type WorkspaceFileRenameInput = { path: string; newPath: string }

export type ResizeStart = (event: PointerEvent<HTMLElement>) => void

export function ChallengeSidebar({
  run,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
}: {
  run: ChallengeRun
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<ChallengeRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<ChallengeRun>
  onDeleteFile: (path: string) => Promise<ChallengeRun>
  onOpenFile: (path: string | null) => void
}) {
  return (
    <aside
      className="gameplay-workspace__sidebar"
      style={{
        gridTemplateRows: projectFilesOpen
          ? 'minmax(13rem, 0.72fr) minmax(18rem, 0.58fr)'
          : 'minmax(13rem, 1fr) auto',
      }}
      data-testid="workspace-sidebar"
      data-tour-target="level-story"
    >
      <div className="gameplay-panel-scroll app-scrollbar" data-testid="level-context-scroll">
        <ChallengeContextPanel run={run} />
      </div>

      <div className={cn('gameplay-project-region', projectFilesOpen && 'is-open')} data-testid="project-structure-region">
        <ProjectStructurePanel
          snapshot={run.repository_state}
          rootName={run.challenge.slug}
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
  )
}

export function ChallengeDiagramStage({
  run,
  hasTargetDiagram,
  diagramGridRef,
  diagramGridStyle,
  onBeginDiagramResize,
  onKeyboardDiagramResize,
  onResetDiagramResize,
}: {
  run: ChallengeRun
  hasTargetDiagram: boolean
  diagramGridRef: RefObject<HTMLDivElement | null>
  diagramGridStyle: CSSProperties
  onBeginDiagramResize: ResizeStart
  onKeyboardDiagramResize: (delta: number) => void
  onResetDiagramResize: () => void
}) {
  return (
    <div
      ref={diagramGridRef}
      className={cn(
        'challenge-diagram-grid',
        hasTargetDiagram && 'has-target',
      )}
      style={diagramGridStyle}
    >
      <div className="gameplay-pane" data-tour-target="live-dag">
        <LiveDagPanel
          title="Live DAG"
          badge="live"
          snapshot={run.repository_state}
          className="flex h-full min-h-0 flex-col"
          contentClassName="h-full min-h-0 flex-1"
          zoomStorageKey={DAG_ZOOM_KEY}
          animateChanges
          layoutDirection="horizontal"
        />
      </div>
      {hasTargetDiagram ? (
        <>
          <ResizeHandle
            label="Resize diagrams"
            orientation="vertical"
            className="gameplay-resize gameplay-resize--vertical"
            onPointerDown={onBeginDiagramResize}
            onKeyboardResize={onKeyboardDiagramResize}
            onReset={onResetDiagramResize}
          />
          <div className="gameplay-pane" data-tour-target="expected-state">
            <LiveDagPanel
              title="Expected State"
              badge="target"
              snapshot={run.expected_state!}
              className="flex h-full min-h-0 flex-col"
              contentClassName="h-full min-h-0 flex-1"
              zoomStorageKey={DAG_ZOOM_KEY}
              layoutDirection="horizontal"
            />
          </div>
        </>
      ) : null}
      <ChallengeDagLegend />
    </div>
  )
}

export function ChallengeTerminalStage({
  run,
  lines,
  prompt,
  terminalGridRef,
  terminalGridStyle,
  mutationPending,
  onBeginTerminalPaneResize,
  onKeyboardTerminalPaneResize,
  onResetTerminalPaneResize,
  onCommand,
}: {
  run: ChallengeRun
  lines: TerminalLine[]
  prompt: TerminalPrompt
  terminalGridRef: RefObject<HTMLDivElement | null>
  terminalGridStyle: CSSProperties
  mutationPending: boolean
  onBeginTerminalPaneResize: ResizeStart
  onKeyboardTerminalPaneResize: (delta: number) => void
  onResetTerminalPaneResize: () => void
  onCommand: (command: string) => void
}) {
  return (
    <div
      ref={terminalGridRef}
      data-testid="terminal-feedback-grid"
      className={cn(
        'gameplay-terminal-grid',
        run.scaffolding.contextual_feedback && 'has-feedback',
      )}
      style={terminalGridStyle}
    >
      <div className="gameplay-pane" data-tour-target="terminal">
        <TerminalPanel
          lines={lines}
          prompt={prompt}
          disabled={run.status !== 'started'}
          runDisabled={mutationPending}
          processing={mutationPending}
          className="h-full"
          onCommand={onCommand}
        />
      </div>
      {run.scaffolding.contextual_feedback ? (
        <ResizeHandle
          label="Resize terminal and feedback"
          orientation="vertical"
          className="gameplay-resize gameplay-resize--vertical"
          onPointerDown={onBeginTerminalPaneResize}
          onKeyboardResize={onKeyboardTerminalPaneResize}
          onReset={onResetTerminalPaneResize}
        />
      ) : null}
      {run.scaffolding.contextual_feedback ? (
        <div className="gameplay-pane" data-tour-target="feedback">
          <ContextualFeedbackPanel run={run} />
        </div>
      ) : null}
    </div>
  )
}
