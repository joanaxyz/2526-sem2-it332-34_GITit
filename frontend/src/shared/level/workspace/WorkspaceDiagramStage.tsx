import { X } from 'lucide-react'
import { useEffect, useRef } from 'react'

import { Button } from '@/shared/components/Button'
import { DAG_ZOOM_KEY } from '@/shared/level/workspace/layout'
import type { RepoGraphDrawer, WorkspaceRun } from '@/shared/level/workspace/types'
import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'
import { WorkspaceDagLegend } from '@/shared/level/workspace/WorkspaceDagLegend'
import { WorkspaceDagStage } from '@/shared/level/workspace/WorkspaceDagStage'
import { WorkspaceDagTabs } from '@/shared/level/workspace/WorkspaceDagTabs'
import { cn } from '@/shared/utils/cn'
import { useFocusTrap } from '@/shared/utils/useFocusTrap'

export const REPO_GRAPH_ID = 'tier-repo-graph'

/**
 * Right column, driven by run.scaffolding.expected_state. With an Expected
 * State the two diagrams share a tabbed card; without one the Live DAG stands
 * alone under its own title and no tab bar is shown.
 *
 * In drawer mode the same, always-mounted rail becomes a modal dialog: while
 * closed it is moved off screen, transparent and inert (never display:none, so
 * React Flow keeps its size); while open it traps focus and closes on Escape.
 */
export function WorkspaceDiagramStage({
  run,
  animation,
  drawer,
}: {
  run: Pick<WorkspaceRun, 'id' | 'scaffolding' | 'expected_state' | 'repository_state' | 'counts'>
  animation: DagAnimationController
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
        id={REPO_GRAPH_ID}
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
          <WorkspaceDagTabs
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
              <WorkspaceDagStage
                snapshot={run.repository_state}
                animation={animation}
                zoomStorageKey={DAG_ZOOM_KEY}
                className="h-full min-h-0"
                refitKey={drawer?.openCount}
              />
            </div>
            <WorkspaceDagLegend />
          </div>
        )}
      </aside>
    </>
  )
}
