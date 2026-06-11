import { ChevronLeft, ChevronRight } from 'lucide-react'

import { HUB_TABS, type HubTabId } from '@/features/home/hubTabs'

/**
 * Launcher-style sub-tab deck: ‹ Stats · Achievements · Hero Showcase ›.
 * Inactive tabs sit dimmed; the active one lights up with an underline
 * blade. The chevrons cycle through tabs (wrapping at the ends).
 */
export function HubTabs({ active, onSelect }: { active: HubTabId; onSelect: (id: HubTabId) => void }) {
  const index = HUB_TABS.findIndex((t) => t.id === active)

  function cycle(delta: number) {
    const next = (index + delta + HUB_TABS.length) % HUB_TABS.length
    onSelect(HUB_TABS[next].id)
  }

  return (
    <div className="flex items-center justify-center gap-3 max-sm:gap-1.5">
      <button
        type="button"
        className="hub-tab-arrow chamfer-frame"
        aria-label="Previous tab"
        onClick={() => cycle(-1)}
      >
        <span className="chamfer-body">
          <ChevronLeft className="size-4" />
        </span>
      </button>

      <div role="tablist" aria-label="Hub sections" className="flex items-center">
        {HUB_TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            id={`hub-tab-${tab.id}`}
            aria-selected={active === tab.id}
            aria-controls={`hub-panel-${tab.id}`}
            className="hub-tab"
            onClick={() => onSelect(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <button
        type="button"
        className="hub-tab-arrow chamfer-frame"
        aria-label="Next tab"
        onClick={() => cycle(1)}
      >
        <span className="chamfer-body">
          <ChevronRight className="size-4" />
        </span>
      </button>
    </div>
  )
}
