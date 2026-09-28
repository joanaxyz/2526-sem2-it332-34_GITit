/** Shared dynamic import so the start screen can fetch the workspace chunk early. */
export function loadAdventureRunPage() {
  return import('@/features/adventures/pages/AdventureRunPage')
}
