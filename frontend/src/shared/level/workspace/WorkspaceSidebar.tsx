import { ProjectStructurePanel } from '@/shared/level/components/ProjectStructurePanel'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'
import { ContextualFeedbackPanel } from '@/shared/level/workspace/ContextualFeedbackPanel'
import { ObjectivesCard } from '@/shared/level/workspace/ObjectivesCard'
import type { WorkspaceRun, WorkspaceScene } from '@/shared/level/workspace/types'
import { workspaceObjectives } from '@/shared/level/workspace/workspaceObjectives'
import { workspaceStoryContent } from '@/shared/level/workspace/workspaceStory'
import { cn } from '@/shared/utils/cn'

/**
 * Left column: Objectives, Project files, then Contextual feedback.
 *
 * Feedback is part of the difficulty's scaffolding (run.scaffolding.
 * contextual_feedback). Where the difficulty has none the card is not
 * rendered and Project files takes its space. While a command guide teaches
 * on a difficulty with feedback, the card keeps its space so the column does
 * not jump, but its content is hidden: the guide is the feedback then.
 */
export function WorkspaceSidebar({
  run,
  scene,
  teachingActive = false,
  projectFilesOpen,
  workspaceEditorPath,
  createDisabled,
  onToggleProjectFiles,
  onCreateFile,
  onRenameFile,
  onDeleteFile,
  onOpenFile,
  onOpenStory,
}: {
  run: WorkspaceRun
  scene: Pick<WorkspaceScene, 'rootName' | 'title'>
  teachingActive?: boolean
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<unknown>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<unknown>
  onDeleteFile: (path: string) => Promise<unknown>
  onOpenFile: (path: string | null) => void
  onOpenStory?: () => void
}) {
  const hasFeedback = run.scaffolding.contextual_feedback

  return (
    <aside
      className={cn(
        'gameplay-workspace__sidebar tier-sidebar',
        hasFeedback && 'has-feedback',
        !projectFilesOpen && 'is-files-collapsed',
      )}
      data-testid="tier-workspace-sidebar"
      data-tour-target="level-story"
    >
      <div className="gameplay-pane tier-objectives-region">
        <ObjectivesCard
          objectives={workspaceObjectives(run)}
          requiredValues={workspaceStoryContent(run, scene.title).requiredValues}
          onOpenStory={onOpenStory}
        />
      </div>

      <div
        className={cn('gameplay-project-region', projectFilesOpen && 'is-open')}
        data-testid="project-structure-region"
        data-tour-target="project-files"
      >
        <ProjectStructurePanel
          snapshot={run.repository_state}
          rootName={scene.rootName}
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

      {hasFeedback ? (
        <div
          className={cn('gameplay-pane tier-feedback-region', teachingActive && 'is-suspended')}
          data-testid="tier-feedback-region"
          data-tour-target="feedback"
        >
          <ContextualFeedbackPanel run={run} />
        </div>
      ) : null}
    </aside>
  )
}
