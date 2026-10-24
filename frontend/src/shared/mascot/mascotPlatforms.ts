export type MascotPlatform = { element: HTMLElement; left: number; right: number; y: number }

const PLATFORM_SELECTOR = '[data-mascot-platform], section, article, aside, [class*="panel"], [class*="card"], [class*="showcase"], [class*="roster"], [class*="surface"]'

/** Container tops are physical ledges, measured in the viewport overlay's coordinates. */
export function mascotPlatforms(root: HTMLElement, host: DOMRect): MascotPlatform[] {
  const seen = new Set<string>()
  return Array.from(root.querySelectorAll<HTMLElement>(PLATFORM_SELECTOR)).flatMap((element) => {
    const platform = mascotPlatform(element, root, host)
    if (!platform) return []
    const key = `${Math.round(platform.left)}:${Math.round(platform.right)}:${Math.round(platform.y)}`
    if (seen.has(key)) return []
    seen.add(key)
    return [platform]
  })
}

export function mascotPlatform(element: HTMLElement, root: HTMLElement, host: DOMRect, perch = false): MascotPlatform | null {
  if (!element.isConnected || element.closest('.world-mascot, [hidden], [inert], [aria-hidden="true"], [role="dialog"]')) return null
  const rect = element.getBoundingClientRect()
  const style = getComputedStyle(element)
  const explicit = perch || element.matches('[data-mascot-platform]')
  if (rect.width < (explicit ? 28 : 70) || rect.height < 20 || rect.top < 65 || rect.top > innerHeight - 35 || style.visibility === 'hidden' || style.display === 'none') return null
  const painted = parseFloat(style.borderTopWidth) > 0 ||
    !['transparent', 'rgba(0, 0, 0, 0)', ''].includes(style.backgroundColor) || style.backgroundImage !== 'none'
  if (!painted && !element.matches('[data-mascot-platform], section, article, aside')) return null
  let left = Math.max(28, rect.left - host.left)
  let right = Math.min(host.width - 28, rect.right - host.left)
  // Scrollable rails can contain offscreen panels; only their visible top edges count.
  for (let ancestor = element.parentElement; ancestor && root.contains(ancestor); ancestor = ancestor.parentElement) {
    const overflow = getComputedStyle(ancestor)
    const clipsX = /auto|scroll|hidden|clip/.test(overflow.overflowX)
    const clipsY = /auto|scroll|hidden|clip/.test(overflow.overflowY)
    if (!clipsX && !clipsY) continue
    const clip = ancestor.getBoundingClientRect()
    if (clipsY && (rect.top < clip.top - 1 || rect.top > clip.bottom)) return null
    if (clipsX) { left = Math.max(left, clip.left - host.left); right = Math.min(right, clip.right - host.left) }
  }
  const y = rect.top - host.top
  if (right - left < (explicit ? 28 : 45)) return null
  return { element, left, right, y }
}

/** Clicking any part of a node or button lands at the center of its top, so the guide never covers it. */
export function mascotPerch(root: HTMLElement, host: DOMRect, target: Element): MascotPlatform | null {
  const node = target.closest<HTMLElement>('[data-mascot-perch], button:not(:disabled)')
  if (!node || !root.contains(node)) return null
  const ring = node.querySelector<HTMLElement>('[data-mascot-platform]') ?? node
  return mascotPlatform(ring, root, host, true)
}

export function platformNear(platforms: MascotPlatform[], x: number, y: number): MascotPlatform | null {
  return platforms.filter((platform) => x >= platform.left && x <= platform.right && Math.abs(y - platform.y) <= 65)
    .sort((a, b) => Math.abs(a.y - y) - Math.abs(b.y - y) || (a.right - a.left) - (b.right - b.left))[0] ?? null
}

export function mascotTilt(dx: number, dy: number): number {
  const angle = Math.atan2(dy, Math.max(90, Math.abs(dx))) * 180 / Math.PI
  return Math.max(-30, Math.min(30, angle * (dx < 0 ? -1 : 1)))
}
