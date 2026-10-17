import { X } from 'lucide-react'
import { useEffect, useRef } from 'react'

import { TierDagStage } from '@/features/story-map/components/TierDagStage'
import { TierDagLegend } from '@/features/story-map/components/TierDagLegend'
import { TierDagTabs } from '@/features/story-map/components/tier-workspace/TierDagTabs'
import { DAG_ZOOM_KEY } from '@/features/story-map/components/tierWorkspaceLayout'
import type { TierRun } from '@/features/story-map/components/tierWorkspaceTypes'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'
import { useFocusTrap } from '@/shared/utils/useFocusTrap'

export const TIER_REPO_GRAPH_ID = 'tier-repo-graph'

/** Set while the layout shows the graph as a slide-over drawer (700-1099px). */
type RepoGraphDrawer = {
  open: boolean
  /** Increments on every opening, so the diagrams refit as they appear. */
  openCount: number
  onClose: () => void
}

/**
 * Right column. With an Expected State (Easy) the two diagrams share a tabbed
 * card; without one (Medium, Hard) the Live DAG stands alone under its own
 * title and no tab bar is shown.
 *
 * In drawer mode the same, always-mounted rail becomes a modal dialog: while
 * closed it is moved off screen, transparent and inert (never display:none, so
 * React Flow keeps its size); while open it traps focus and closes on Escape.
 */
export function TierDiagramStage({
  run,
  animation,
  drawer,
}: {
  run: TierRun
  animation: TierDagAnimationController
  drawer?: RepoGraphDrawer
}) {
  const railRef = useRef<HTMLElement>(null)
  const expectedState = run.scaffolding.expected_state ? run.expected_state : null
  const open = Boolean(drawer?.open)
  const onClose = drawer?.onClose
  useFocusTrap(railRef, open)

  useEffect(() => {
    if (!open || !onClose) return
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== 'Escape') return
      event.preventDefault()
      onClose?.()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [open, onClose])

  const drawerProps = drawer
    ? {
        role: 'dialog',
        'aria-modal': open || undefined,
        'aria-label': 'Repository graph',
        tabIndex: -1,
        inert: !open,
      }
    : {}

  return (
    <>
      {open ? <div className="tier-dag-backdrop" aria-hidden="true" onClick={onClose} /> : null}
      <aside
        ref={railRef}
        id={TIER_REPO_GRAPH_ID}
        className={cn('tier-dag-rail', drawer && 'is-drawer', drawer && (open ? 'is-open' : 'is-closed'))}
        {...drawerProps}
      >
        {drawer ? (
          <div className="tier-dag-drawer-header">
            <span className="panel-eyebrow">Repository graph</span>
            <Button type="button" variant="ghost" size="icon" aria-label="Close repository graph" onClick={drawer.onClose}>
              <X aria-hidden="true" />
            </Button>
          </div>
        ) : null}
        {expectedState ? (
          <TierDagTabs
            key={run.id}
            snapshot={run.repository_state}
            expectedState={expectedState}
            countedCommands={run.counts.counted_action_total}
            animation={animation}
            refitToken={drawer?.openCount}
            tourAnchors={!drawer}
          />
        ) : (
          <div className="tier-repository-view">
            <div className="gameplay-pane" data-tour-target={drawer ? undefined : 'live-dag'}>
              <TierDagStage
                snapshot={run.repository_state}
                animation={animation}
                zoomStorageKey={DAG_ZOOM_KEY}
                className="h-full min-h-0"
                refitKey={drawer?.openCount}
              />
            </div>
            <TierDagLegend />
          </div>
        )}
      </aside>
    </>
  )
}
