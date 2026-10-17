import { useId, useRef, useState } from 'react'
import type { KeyboardEvent } from 'react'

import { TierDagStage } from '@/features/story-map/components/TierDagStage'
import { TierDagLegend } from '@/features/story-map/components/TierDagLegend'
import { DAG_ZOOM_KEY } from '@/features/story-map/components/tierWorkspaceLayout'
import type { TierDagAnimationController } from '@/features/story-map/hooks/useTierDagAnimation'
import { LiveDagPanel } from '@/shared/level/components/LiveDagPanel'
import type { RepositorySnapshot } from '@/shared/level/types'
import { cn } from '@/shared/utils/cn'

type DagTab = 'live' | 'expected'

const TABS: { id: DagTab; label: string }[] = [
  { id: 'live', label: 'Live DAG' },
  { id: 'expected', label: 'Expected state' },
]

/**
 * Live DAG and Expected State share one card behind tabs. Both React Flow
 * views stay mounted at the same size: the inactive pane is made transparent
 * and inert, so its measured size, zoom and pan survive, and it is refit when
 * shown. A counted command brings the learner back to the Live DAG, since
 * that is where its result appears.
 */
export function TierDagTabs({
  snapshot,
  expectedState,
  countedCommands,
  animation,
  refitToken,
  tourAnchors = true,
}: {
  snapshot: RepositorySnapshot
  expectedState: RepositorySnapshot
  /** The run's counted-command total; an increase switches back to the Live DAG. */
  countedCommands: number
  animation: TierDagAnimationController
  /** Changes when the host reveals the card (e.g. a drawer opening); both views refit. */
  refitToken?: number
  /** Off while the card sits in a closed drawer, where the tour cannot point at it. */
  tourAnchors?: boolean
}) {
  const baseId = useId()
  const [active, setActive] = useState<DagTab>('live')
  const [activations, setActivations] = useState<Record<DagTab, number>>({ live: 0, expected: 0 })
  const [seenCountedCommands, setSeenCountedCommands] = useState(countedCommands)
  const tabRefs = useRef<Record<DagTab, HTMLButtonElement | null>>({ live: null, expected: null })
  const tabId = (tab: DagTab) => `${baseId}-${tab}-tab`
  const panelId = (tab: DagTab) => `${baseId}-${tab}-panel`

  const select = (tab: DagTab) => {
    if (tab === active) return
    setActive(tab)
    setActivations((counts) => ({ ...counts, [tab]: counts[tab] + 1 }))
  }

  // Adjusted during render (React's pattern for state derived from a changing
  // prop), so the switch lands in the same commit as the new repository state.
  if (countedCommands !== seenCountedCommands) {
    setSeenCountedCommands(countedCommands)
    if (countedCommands > seenCountedCommands) select('live')
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
    role: 'tabpanel',
    id: panelId(tab),
    'aria-labelledby': tabId(tab),
    className: cn('gameplay-pane tier-dag-pane', active === tab ? 'is-active' : 'is-inactive'),
    inert: active !== tab,
  })

  return (
    <section className="tier-dag-tabs" aria-label="Repository diagrams">
      <div className="tier-dag-tablist workspace-panel-header">
        <div className="tier-dag-toggle" role="tablist" aria-label="Repository view" data-active={active}>
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
      </div>

      <div className="tier-dag-panes">
        <div {...paneProps('live')} data-tour-target={tourAnchors ? 'live-dag' : undefined}>
          <TierDagStage
            snapshot={snapshot}
            animation={animation}
            zoomStorageKey={DAG_ZOOM_KEY}
            className="h-full min-h-0"
            showHeader={false}
            refitKey={`${activations.live}:${refitToken ?? 0}`}
          />
        </div>
        <div {...paneProps('expected')}>
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
          />
        </div>
        <TierDagLegend />
      </div>
    </section>
  )
}
