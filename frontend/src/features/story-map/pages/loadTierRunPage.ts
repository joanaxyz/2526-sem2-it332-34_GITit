/** Shared dynamic import so the start screen can fetch the workspace chunk early. */
export function loadTierRunPage() {
  return import('@/features/story-map/pages/TierRunPage')
}
