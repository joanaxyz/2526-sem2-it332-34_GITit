import { useId, useLayoutEffect, useRef, useState } from 'react'
import type { CSSProperties, KeyboardEvent, PointerEvent } from 'react'

import { WorkspaceDagStage } from '@/shared/level/workspace/WorkspaceDagStage'
import { WorkspaceDagLegend } from '@/shared/level/workspace/WorkspaceDagLegend'
import { DAG_ZOOM_KEY } from '@/shared/level/workspace/layout'
import type { DagAnimationController } from '@/shared/level/workspace/useDagAnimation'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import type { RepositorySnapshot } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

type DagTab = 'live' | 'expected'
type DagViewMode = 'switch' | 'split'

const MIN_SPLIT_PERCENT = 0
const MAX_SPLIT_PERCENT = 100
const DEFAULT_SPLIT_PERCENT = 50

const TABS: { id: DagTab; label: string }[] = [
  { id: 'live', label: 'Live' },
  { id: 'expected', label: 'Expected' },
]

/**
 * Live DAG and Expected State share one card. Switch mode keeps the existing
 * tabs; split mode stacks both diagrams and lets the learner resize their
 * viewports without changing either graph's zoom or pan.
 */
export function WorkspaceDagTabs({
  snapshot,
  expectedState,
  countedCommands,
  animation,
  refitToken,
  tourAnchors = true,
}: {
  snapshot: RepositorySnapshot
  expectedState: RepositorySnapshot
  /** The run's counted-command total; an increase selects the Live DAG. */
  countedCommands: number
  animation: DagAnimationController
  /** Changes when the host reveals the card (e.g. a drawer opening); both views refit. */
  refitToken?: number
  /** Off while the card sits in a closed drawer, where the tour cannot point at it. */
  tourAnchors?: boolean
}) {
  const baseId = useId()
  const [active, setActive] = useState<DagTab>('live')
  const [viewMode, setViewMode] = useState<DagViewMode>('switch')
  const [splitPercent, setSplitPercent] = useState(DEFAULT_SPLIT_PERCENT)
  const [activations, setActivations] = useState<Record<DagTab, number>>({ live: 0, expected: 0 })
  const [seenCountedCommands, setSeenCountedCommands] = useState(countedCommands)
  const tabRefs = useRef<Record<DagTab, HTMLButtonElement | null>>({ live: null, expected: null })
  const splitterDrag = useRef<{ pointerId: number; startY: number; startPercent: number; availableHeight: number } | null>(null)
  const panesRef = useRef<HTMLDivElement | null>(null)
  const [splitMetrics, setSplitMetrics] = useState({ height: 0, splitterHeight: 0 })
  const liveRowHeight = ((splitMetrics.height - splitMetrics.splitterHeight) * splitPercent) / 100
  const tabId = (tab: DagTab) => `${baseId}-${tab}-tab`
  const panelId = (tab: DagTab) => `${baseId}-${tab}-panel`

  const select = (tab: DagTab) => {
    if (tab === active && viewMode === 'switch') return
    setViewMode('switch')
    if (tab !== active) {
      setActive(tab)
      setActivations((counts) => ({ ...counts, [tab]: counts[tab] + 1 }))
    }
  }

  // Adjusted during render (React's pattern for state derived from a changing
  // prop), so the switch lands in the same commit as the new repository state.
  if (countedCommands !== seenCountedCommands) {
    setSeenCountedCommands(countedCommands)
    if (countedCommands > seenCountedCommands) {
      if (viewMode === 'split') setActive('live')
      else select('live')
    }
  }

  useLayoutEffect(() => {
    if (viewMode !== 'split' || !panesRef.current) return
    const panes = panesRef.current
    const measure = () => {
      const height = panes.getBoundingClientRect().height
      const splitterHeight = panes.querySelector('.tier-dag-splitter')?.getBoundingClientRect().height ?? 0
      setSplitMetrics((current) => current.height === height && current.splitterHeight === splitterHeight
        ? current
        : { height, splitterHeight })
    }
    measure()
    if (typeof ResizeObserver === 'undefined') {
      window.addEventListener('resize', measure)
      return () => window.removeEventListener('resize', measure)
    }
    const observer = new ResizeObserver(measure)
    observer.observe(panes)
    return () => observer.disconnect()
  }, [viewMode])

  const onSplitterPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (event.button !== 0) return
    const panes = event.currentTarget.parentElement
    if (!panes) return
    const panesHeight = panes.getBoundingClientRect().height
    const handleHeight = event.currentTarget.getBoundingClientRect().height
    splitterDrag.current = {
      pointerId: event.pointerId,
      startY: event.clientY,
      startPercent: splitPercent,
      availableHeight: Math.max(1, panesHeight - handleHeight),
    }
    event.preventDefault()
    event.stopPropagation()
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const onSplitterPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const drag = splitterDrag.current
    if (!drag || drag.pointerId !== event.pointerId) return
    const deltaPercent = ((event.clientY - drag.startY) / drag.availableHeight) * 100
    setSplitPercent(clampSplitPercent(drag.startPercent + deltaPercent))
  }

  const stopSplitterDrag = (event: PointerEvent<HTMLDivElement>) => {
    if (splitterDrag.current?.pointerId === event.pointerId) splitterDrag.current = null
  }

  const onSplitterKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const adjustment = event.shiftKey ? 5 : 2
    const next = event.key === 'ArrowUp' ? splitPercent - adjustment
      : event.key === 'ArrowDown' ? splitPercent + adjustment
        : event.key === 'Home' ? MIN_SPLIT_PERCENT
          : event.key === 'End' ? MAX_SPLIT_PERCENT
            : null
    if (next === null) return
    event.preventDefault()
    setSplitPercent(clampSplitPercent(next))
  }

  // WAI-ARIA tabs: arrows (and Home/End) move between tabs and select them.
  const onTabKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    const index = TABS.findIndex((tab) => tab.id === active)
    const next =
      event.key === 'ArrowRight' ? TABS[(index + 1) % TABS.length]
        : event.key === 'ArrowLeft' ? TABS[(index - 1 + TABS.length) % TABS.length]
          : event.key === 'Home' ? TABS[0]
            : event.key === 'End' ? TABS[TABS.length - 1]
              : null
    if (!next) return
    event.preventDefault()
    select(next.id)
    tabRefs.current[next.id]?.focus()
  }

  const paneProps = (tab: DagTab) => ({
    role: viewMode === 'split' ? 'region' : 'tabpanel',
    id: panelId(tab),
    ...(viewMode === 'split'
      ? { 'aria-label': tab === 'live' ? 'Live DAG' : 'Expected state' }
      : { 'aria-labelledby': tabId(tab) }),
    className: cn(
      'gameplay-pane tier-dag-pane',
      viewMode === 'split' ? 'is-split' : active === tab ? 'is-active' : 'is-inactive',
    ),
    inert: viewMode !== 'split' && active !== tab,
    'data-dag-pane': tab,
  })

  return (
    <section className={cn('tier-dag-tabs', viewMode === 'split' && 'is-split')} aria-label="Repository diagrams">
      <div className="tier-dag-controls">
        <div className="tier-dag-toggle tier-dag-layout-toggle" role="group" aria-label="DAG display mode" data-active={viewMode}>
          <button
            type="button"
            className="tier-dag-tab"
            aria-pressed={viewMode === 'switch'}
            onClick={() => setViewMode('switch')}
          >
            Switch
          </button>
          <button
            type="button"
            className="tier-dag-tab"
            aria-pressed={viewMode === 'split'}
            onClick={() => setViewMode('split')}
          >
            Split
          </button>
        </div>
        {viewMode === 'switch' ? (
          <div className="tier-dag-toggle tier-dag-view-toggle" role="tablist" aria-label="Repository view" data-active={active}>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                ref={(element) => {
                  tabRefs.current[tab.id] = element
                }}
                type="button"
                role="tab"
                id={tabId(tab.id)}
                className="tier-dag-tab"
                aria-selected={active === tab.id}
                aria-controls={panelId(tab.id)}
                tabIndex={active === tab.id ? 0 : -1}
                data-tour-target={tourAnchors && tab.id === 'expected' ? 'expected-state' : undefined}
                onClick={() => select(tab.id)}
                onKeyDown={onTabKeyDown}
              >
                {tab.label}
              </button>
            ))}
          </div>
        ) : null}
      </div>

      <div
        ref={panesRef}
        className={cn('tier-dag-panes', viewMode === 'split' && 'is-split')}
        style={viewMode === 'split'
          ? {
              gridTemplateRows: `minmax(0, ${splitPercent}fr) 0.55rem minmax(0, ${100 - splitPercent}fr)`,
              // Both canvases span the whole split area and each pane only
              // clips them, so dragging moves the divider like a blind
              // without resizing or shifting either graph.
              ...(splitMetrics.height > 0
                ? {
                    '--tier-dag-split-height': `${splitMetrics.height}px`,
                    '--tier-dag-expected-hidden': `${liveRowHeight + splitMetrics.splitterHeight}px`,
                  } as CSSProperties
                : {}),
            }
          : undefined}
      >
        <div {...paneProps('live')} data-tour-target={tourAnchors ? 'live-dag' : undefined}>
          <WorkspaceDagStage
            snapshot={snapshot}
            animation={animation}
            zoomStorageKey={DAG_ZOOM_KEY}
            className="h-full min-h-0"
            showHeader={false}
            refitKey={`${activations.live}:${refitToken ?? 0}`}
            preserveViewportOnResize
          />
        </div>
        {viewMode === 'split' ? (
          <div
            className="tier-dag-splitter"
            role="separator"
            aria-label="Resize Live DAG and Expected State"
            aria-orientation="horizontal"
            aria-valuemin={MIN_SPLIT_PERCENT}
            aria-valuemax={MAX_SPLIT_PERCENT}
            aria-valuenow={Math.round(splitPercent)}
            aria-valuetext={`Live DAG ${Math.round(splitPercent)}%, Expected state ${Math.round(100 - splitPercent)}%`}
            tabIndex={0}
            onPointerDown={onSplitterPointerDown}
            onPointerMove={onSplitterPointerMove}
            onPointerUp={stopSplitterDrag}
            onPointerCancel={stopSplitterDrag}
            onLostPointerCapture={stopSplitterDrag}
            onKeyDown={onSplitterKeyDown}
          />
        ) : null}
        <div
          {...paneProps('expected')}
          data-tour-target={tourAnchors && viewMode === 'split' ? 'expected-state' : undefined}
        >
          <LiveDagPanel
            title="Expected State"
            snapshot={expectedState}
            className="flex h-full min-h-0 flex-col"
            contentClassName="h-full min-h-0 flex-1"
            zoomStorageKey={`${DAG_ZOOM_KEY}:expected`}
            fitViewPadding={0.16}
            layoutDirection="vertical"
            showHeader={false}
            refitKey={`${activations.expected}:${refitToken ?? 0}`}
            preserveViewportOnResize
          />
        </div>
        <WorkspaceDagLegend />
      </div>
    </section>
  )
}

function clampSplitPercent(value: number) {
  return Math.min(MAX_SPLIT_PERCENT, Math.max(MIN_SPLIT_PERCENT, value))
}
