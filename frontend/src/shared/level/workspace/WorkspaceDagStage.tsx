import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import type { RepositorySnapshot } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

export function WorkspaceDagStage({
  snapshot,
  animation,
  zoomStorageKey,
  className,
  showHeader,
  refitKey,
  preserveViewportOnResize = false,
}: {
  snapshot: RepositorySnapshot
  animation: DagAnimationController
  zoomStorageKey: string
  className?: string
  showHeader?: boolean
  refitKey?: string | number
  preserveViewportOnResize?: boolean
}) {
  return (
    <section
      className={cn('challenge-dag-stage', `is-${animation.activity}`, className)}
      data-dag-activity={animation.activity}
      data-testid="tier-dag-stage"
      aria-label="Repository puzzle stage"
    >
      <LiveDagPanel
        title="Live DAG"
        snapshot={snapshot}
        className="flex h-full min-h-0 flex-col"
        contentClassName="h-full min-h-0 flex-1"
        zoomStorageKey={zoomStorageKey}
        fitViewPadding={0.16}
        animateChanges
        activity={animation.activity}
        layoutDirection="vertical"
        showHeader={showHeader}
        refitKey={refitKey}
        preserveViewportOnResize={preserveViewportOnResize}
      />
    </section>
  )
}
