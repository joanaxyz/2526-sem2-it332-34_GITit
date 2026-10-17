import { TierDagStage } from '@/features/story-map/components/TierDagStage'
import { TierDagLegend } from '@/features/story-map/components/TierDagLegend'
import { DAG_ZOOM_KEY } from '@/features/story-map/components/tierWorkspaceLayout'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import { cn } from '@/shared/utils/cn'

export function TierDiagramStage({
  run,
  animation,
}: {
  run: TierRun
  animation: TierDagAnimationController
}) {
  const hasTargetDiagram = Boolean(run.scaffolding.expected_state && run.expected_state)

  return (
    <aside className="tier-dag-rail">
      <div
        id="tier-live-dag-panel"
        className={cn('tier-repository-view', hasTargetDiagram && 'has-target')}
      >
        <div className="gameplay-pane" data-tour-target="live-dag">
          <TierDagStage
            snapshot={run.repository_state}
            animation={animation}
            zoomStorageKey={DAG_ZOOM_KEY}
            className="h-full min-h-0"
          />
        </div>
        {hasTargetDiagram ? (
          <div className="gameplay-pane" data-tour-target="expected-state">
            <LiveDagPanel
              title="Expected State"
              snapshot={run.expected_state!}
              className="flex h-full min-h-0 flex-col"
              contentClassName="h-full min-h-0 flex-1"
              zoomStorageKey={`${DAG_ZOOM_KEY}:expected`}
              fitViewPadding={0.16}
              layoutDirection="vertical"
            />
          </div>
        ) : null}
        <TierDagLegend />
      </div>
    </aside>
  )
}
