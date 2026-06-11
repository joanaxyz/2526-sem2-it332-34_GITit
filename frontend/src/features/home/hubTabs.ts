export type HubTabId = 'stats' | 'achievements' | 'showcase'

/** Hero Showcase is the default tab and sits at the center of the deck. */
export const HUB_TABS: { id: HubTabId; label: string }[] = [
  { id: 'stats', label: 'Stats' },
  { id: 'showcase', label: 'Hero Showcase' },
  { id: 'achievements', label: 'Achievements' },
]

export const DEFAULT_HUB_TAB: HubTabId = 'showcase'
