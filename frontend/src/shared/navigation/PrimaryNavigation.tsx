import { Compass, GitBranch, ShieldCheck, Store, type LucideIcon } from 'lucide-react'
import { useCallback, useEffect, useLayoutEffect, useRef } from 'react'
import { NavLink, useLocation } from 'react-router-dom'

import { useAuthStore } from '@/shared/auth/useAuth'
import { ADMIN_ROUTES, HOME_ROUTE, SHOP_ROUTE, isStoryMapRoute, storyPath } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'

type PrimaryNavItem = {
  to: string
  label: string
  Icon: LucideIcon
  match: (pathname: string) => boolean
}

const primaryNavItems: PrimaryNavItem[] = [
  {
    to: HOME_ROUTE,
    label: 'Dashboard',
    Icon: Compass,
    match: (pathname) => pathname === '/' || pathname.startsWith(HOME_ROUTE),
  },
  {
    // Land on the default story map; in-page story controls handle switching.
    to: storyPath(),
    label: 'Modules',
    Icon: GitBranch,
    match: isStoryMapRoute,
  },
  {
    to: SHOP_ROUTE,
    label: 'Shop',
    Icon: Store,
    match: (pathname) => pathname.startsWith(SHOP_ROUTE),
  },
]

const adminNavItem: PrimaryNavItem = {
  to: ADMIN_ROUTES.dashboard,
  label: 'Admin',
  Icon: ShieldCheck,
  match: (pathname) => pathname.startsWith(ADMIN_ROUTES.dashboard),
}

/**
 * Drives the light that travels between nav items. The active link is measured
 * against its own nav, so one indicator serves both the desktop blade and the
 * mobile bar however many items (admin included) are rendered.
 */
function useTravelingIndicator(itemCount: number) {
  const navRef = useRef<HTMLElement | null>(null)
  const location = useLocation()

  const measure = useCallback(() => {
    const nav = navRef.current
    if (!nav) return

    const active = nav.querySelector<HTMLElement>('[aria-current="page"]')
    if (!active || active.offsetWidth === 0) {
      nav.style.setProperty('--nav-light-opacity', '0')
      return
    }

    nav.style.setProperty('--nav-light-x', `${active.offsetLeft}px`)
    nav.style.setProperty('--nav-light-w', `${active.offsetWidth}px`)
    nav.style.setProperty('--nav-light-opacity', '1')

    // The first placement must not animate in from the left edge; travel is
    // armed one frame later, once the light already sits on the active item.
    if (!nav.dataset.travel) {
      requestAnimationFrame(() => {
        if (navRef.current) navRef.current.dataset.travel = 'on'
      })
    }
  }, [])

  useLayoutEffect(() => {
    measure()
  }, [measure, location.pathname, itemCount])

  useEffect(() => {
    const nav = navRef.current
    if (!nav || typeof ResizeObserver === 'undefined') return

    const observer = new ResizeObserver(() => measure())
    observer.observe(nav)
    return () => observer.disconnect()
  }, [measure])

  // Label widths shift when the interface font finishes loading.
  useEffect(() => {
    const fonts = document.fonts
    if (!fonts?.ready) return

    let cancelled = false
    void fonts.ready.then(() => {
      if (!cancelled) measure()
    })
    return () => {
      cancelled = true
    }
  }, [measure])

  return navRef
}

export type PrimaryNavProps = {
  includeAdmin?: boolean
  navClassName: string
  linkClassName: string
  activeClassName?: string
}

export function PrimaryNav({
  includeAdmin = false,
  navClassName,
  linkClassName,
  activeClassName = 'is-active',
}: PrimaryNavProps) {
  const location = useLocation()
  const navItems = includeAdmin ? [...primaryNavItems, adminNavItem] : primaryNavItems
  const navRef = useTravelingIndicator(navItems.length)

  return (
    <nav ref={navRef} className={navClassName} aria-label="Primary">
      <span className="app-nav-light" aria-hidden="true" />
      {navItems.map(({ to, label, Icon, match }) => {
        const matchesCurrentPath = match(location.pathname)

        return (
          <NavLink
            key={to}
            aria-current={matchesCurrentPath ? 'page' : undefined}
            className={({ isActive }) =>
              cn(linkClassName, (isActive || matchesCurrentPath) && activeClassName)
            }
            to={to}
          >
            <Icon aria-hidden="true" />
            <span className="app-nav-link-label">{label}</span>
          </NavLink>
        )
      })}
    </nav>
  )
}

export function CurrentUserPrimaryNav(props: Omit<PrimaryNavProps, 'includeAdmin'>) {
  const user = useAuthStore((state) => state.user)

  return <PrimaryNav {...props} includeAdmin={Boolean(user?.is_staff)} />
}
