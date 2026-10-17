import { TierContextualFeedbackPanel } from '@/features/story-map/components/TierContextualFeedbackPanel'
import { TierObjectivesCard } from '@/features/story-map/components/tier-workspace/TierObjectivesCard'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import { tierObjectives } from '@/features/story-map/utils/tierObjectives'
import { tierStoryContent } from '@/features/story-map/utils/tierStory'
import { ProjectStructurePanel } from '@/shared/level/components/ProjectStructurePanel'
import type {
  WorkspaceFileInput,
  WorkspaceFileRenameInput,
} from '@/shared/level/workspaceFileTypes'
import { cn } from '@/shared/utils/cn'

/**
 * Left column: Objectives, Project files, then Contextual feedback.
 *
 * Feedback is part of the difficulty's scaffolding (run.scaffolding.
 * contextual_feedback, Easy only). Where the difficulty has none (Medium,
 * Hard) the card is not rendered and Project files takes its space. While a
 * command guide teaches on a difficulty with feedback, the card keeps its
 * space so the column does not jump, but its content is hidden: the guide is
 * the feedback then.
 */
export function TierSidebar({
  run,
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
  run: TierRun
  teachingActive?: boolean
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<TierRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<TierRun>
  onDeleteFile: (path: string) => Promise<TierRun>
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
        <TierObjectivesCard
          objectives={tierObjectives(run)}
          requiredValues={tierStoryContent(run).requiredValues}
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
          rootName={run.tier.adventure_level_slug}
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
          <TierContextualFeedbackPanel run={run} />
        </div>
      ) : null}
    </aside>
  )
}
