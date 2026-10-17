import { TierDagStage } from '@/features/story-map/components/TierDagStage'
import { TierDagLegend } from '@/features/story-map/components/TierDagLegend'
import { TierDagTabs } from '@/features/story-map/components/tier-workspace/TierDagTabs'
import { DAG_ZOOM_KEY } from '@/features/story-map/components/tierWorkspaceLayout'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'

/**
 * Right column. With an Expected State (Easy) the two diagrams share a tabbed
 * card; without one (Medium, Hard) the Live DAG stands alone under its own
 * title and no tab bar is shown.
 */
export function TierDiagramStage({
  run,
  animation,
}: {
  run: TierRun
  animation: TierDagAnimationController
}) {
  const expectedState = run.scaffolding.expected_state ? run.expected_state : null

  return (
    <aside className="tier-dag-rail">
      {expectedState ? (
        <TierDagTabs
          key={run.id}
          snapshot={run.repository_state}
          expectedState={expectedState}
          countedCommands={run.counts.counted_action_total}
          animation={animation}
        />
      ) : (
        <div id="tier-live-dag-panel" className="tier-repository-view">
          <div className="gameplay-pane" data-tour-target="live-dag">
            <TierDagStage
              snapshot={run.repository_state}
              animation={animation}
              zoomStorageKey={DAG_ZOOM_KEY}
              className="h-full min-h-0"
            />
          </div>
          <TierDagLegend />
        </div>
      )}
    </aside>
  )
}
