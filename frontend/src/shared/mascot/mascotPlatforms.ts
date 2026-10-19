export type MascotPlatform = { element: HTMLElement; left: number; right: number; y: number }

const PLATFORM_SELECTOR = '[data-mascot-platform], section, article, aside, [class*="panel"], [class*="card"], [class*="showcase"], [class*="roster"], [class*="surface"]'

/** Container tops are physical ledges, measured in the mascot host's coordinates. */
export function mascotPlatforms(root: HTMLElement, host: DOMRect): MascotPlatform[] {
  const seen = new Set<string>()
  return Array.from(root.querySelectorAll<HTMLElement>(PLATFORM_SELECTOR)).flatMap((element) => {
    if (element.closest('.world-mascot, [hidden], [inert], [role="dialog"]')) return []
    const rect = element.getBoundingClientRect()
    const style = getComputedStyle(element)
    if (rect.width < 70 || rect.height < 28 || rect.top < 65 || rect.top > innerHeight - 35 || style.visibility === 'hidden' || style.display === 'none') return []
    const painted = parseFloat(style.borderTopWidth) > 0 ||
      !['transparent', 'rgba(0, 0, 0, 0)', ''].includes(style.backgroundColor) || style.backgroundImage !== 'none'
    if (!painted && !element.matches('[data-mascot-platform], section, article, aside')) return []
    const left = Math.max(28, rect.left - host.left)
    const right = Math.min(host.width - 28, rect.right - host.left)
    const y = rect.top - host.top
    const key = `${Math.round(left)}:${Math.round(right)}:${Math.round(y)}`
    if (right - left < 45 || seen.has(key)) return []
    seen.add(key)
    return [{ element, left, right, y }]
  })
}

export function platformNear(platforms: MascotPlatform[], x: number, y: number): MascotPlatform | null {
  return platforms.filter((platform) => x >= platform.left && x <= platform.right && Math.abs(y - platform.y) <= 65)
    .sort((a, b) => Math.abs(a.y - y) - Math.abs(b.y - y) || (a.right - a.left) - (b.right - b.left))[0] ?? null
}

export function mascotTilt(dx: number, dy: number): number {
  const angle = Math.atan2(dy, Math.max(90, Math.abs(dx))) * 180 / Math.PI
  return Math.max(-30, Math.min(30, angle * (dx < 0 ? -1 : 1)))
}
