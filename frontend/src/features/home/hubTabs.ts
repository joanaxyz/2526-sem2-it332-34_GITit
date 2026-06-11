export type HubTabId = 'stats' | 'achievements' | 'showcase'

export const HUB_TABS: { id: HubTabId; label: string }[] = [
  { id: 'stats', label: 'Stats' },
  { id: 'achievements', label: 'Achievements' },
  { id: 'showcase', label: 'Hero Showcase' },
]
