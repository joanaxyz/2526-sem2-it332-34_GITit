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

export function TierSidebar({
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
  run: TierRun
  projectFilesOpen: boolean
  workspaceEditorPath: string | null
  createDisabled: boolean
  onToggleProjectFiles: () => void
  onCreateFile: (input: WorkspaceFileInput) => Promise<TierRun>
  onRenameFile: (input: WorkspaceFileRenameInput) => Promise<TierRun>
  onDeleteFile: (path: string) => Promise<TierRun>
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
      data-testid="tier-workspace-sidebar"
      data-tour-target="level-story"
    >
      <div className="gameplay-pane tier-objectives-region">
        <TierObjectivesCard
          objectives={tierObjectives(run)}
          requiredValues={tierStoryContent(run).requiredValues}
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
    </aside>
  )
}
