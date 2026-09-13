import { useQueryClient } from '@tanstack/react-query'
import {
  ChevronDown,
  Compass,
  LogOut,
  Settings,
  ShieldCheck,
  GitBranch,
  Store,
  type LucideIcon,
} from 'lucide-react'
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'

import gitLogoImage from '@/assets/images/GIT_logo.webp'
import { AudioControls } from '@/shared/audio/AudioControls'
import { authApi } from '@/shared/auth/authApi'
import { useRank } from '@/shared/progress/rank'
import type { User } from '@/shared/auth/types'
import { useAuthStore } from '@/shared/auth/useAuth'
import { GitCoinIcon } from '@/shared/wallet/components/GitCoinIcon'
import { useWalletSummary } from '@/shared/wallet/hooks/useWallet'
import { usePlayerLoadout } from '@/shared/player-loadout/usePlayerLoadout'
import { ADMIN_ROUTES, HOME_ROUTE, SHOP_ROUTE, isStoryMapRoute, storyPath } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'
import { useFocusTrap } from '@/shared/utils/useFocusTrap'

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

function formatBalance(balance: number, isPending?: boolean) {
  return isPending ? '---' : balance.toLocaleString()
}

function getInitials(username: string) {
  return (username?.slice(0, 2) || '??').toUpperCase()
}

function useAppLogout() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const clearSession = useAuthStore((state) => state.clearSession)

  return useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      queryClient.clear()
      clearSession()
      navigate('/login')
    }
  }, [clearSession, navigate, queryClient])
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

/** True once the page has left the top, so the bar can earn its elevation. */
function useScrolledPast(threshold = 8) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    let frame = 0
    const read = () => {
      frame = 0
      setScrolled(window.scrollY > threshold)
    }
    const onScroll = () => {
      if (!frame) frame = requestAnimationFrame(read)
    }

    read()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (frame) cancelAnimationFrame(frame)
    }
  }, [threshold])

  return scrolled
}

type PrimaryNavProps = {
  includeAdmin?: boolean
  navClassName: string
  linkClassName: string
  activeClassName?: string
}

function PrimaryNav({
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

function CurrentUserPrimaryNav(props: Omit<PrimaryNavProps, 'includeAdmin'>) {
  const user = useAuthStore((state) => state.user)

  return <PrimaryNav {...props} includeAdmin={Boolean(user?.is_staff)} />
}

function ProfileAvatar({
  initials,
  className,
  open,
  src,
}: {
  initials: string
  className: string
  open: boolean
  src?: string
}) {
  return (
    <span className={cn(className, open && 'is-open')} title={initials}>
      {src ? <img src={src} alt="" /> : <span className="app-profile-avatar-initials">{initials}</span>}
    </span>
  )
}

function DropdownItem({
  icon: Icon,
  label,
  danger = false,
  onClick,
}: {
  icon: LucideIcon
  label: string
  danger?: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      className={cn(
        'app-profile-menu-item',
        danger ? 'app-profile-menu-item--danger' : 'app-profile-menu-item--normal',
      )}
      onClick={onClick}
    >
      <Icon aria-hidden="true" />
      {label}
    </button>
  )
}

function ProfileDropdown({
  user,
  onLogout,
  onNavigate,
}: {
  user: User
  onLogout: () => void | Promise<void>
  onNavigate: (to: string) => void
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)
  const rank = useRank()
  const playerLoadout = usePlayerLoadout()
  const initials = getInitials(user.username)
  const displayName = user.username || 'Adventurer'
  const rankLabel = rank ? `Rank ${rank.tier.numeral}` : 'Rank --'
  const avatarSrc = playerLoadout.hasCompanion
    ? playerLoadout.companion.sprites.avatar?.src ??
      playerLoadout.companion.sprites.portrait?.src ??
      playerLoadout.companion.sprites.idle.src
    : undefined

  useEffect(() => {
    if (!open) return

    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [open])

  useFocusTrap(panelRef, open)

  return (
    <div ref={ref} className="app-profile">
      <button
        type="button"
        aria-label={`${open ? 'Close' : 'Open'} account menu for ${displayName}`}
        aria-expanded={open}
        aria-controls="app-profile-menu"
        className="app-profile-trigger"
        onClick={() => setOpen((value) => !value)}
      >
        <ProfileAvatar
          initials={initials}
          className="app-profile-avatar"
          open={open}
          src={avatarSrc}
        />
        <span className="app-profile-copy">
          <strong>{displayName}</strong>
          <span>{rankLabel}</span>
        </span>
        <ChevronDown className={cn(open && 'is-open')} aria-hidden="true" />
      </button>

      {open ? (
        <div ref={panelRef} id="app-profile-menu" className="dropdown-menu app-profile-menu">
          <div className="app-profile-menu-head">
            <div>
              <p>{displayName}</p>
              <span>{user.email}</span>
            </div>
          </div>

          <div className="app-profile-menu-list">
            <DropdownItem
              icon={Settings}
              label="Settings"
              onClick={() => {
                setOpen(false)
                onNavigate('/settings')
              }}
            />
            {user.is_staff ? (
              <DropdownItem
                icon={ShieldCheck}
                label="Admin console"
                onClick={() => {
                  setOpen(false)
                  onNavigate(ADMIN_ROUTES.dashboard)
                }}
              />
            ) : null}
          </div>

          <div className="app-profile-menu-list app-profile-menu-list--bordered">
            <DropdownItem
              icon={LogOut}
              label="Logout"
              danger
              onClick={() => {
                setOpen(false)
                void onLogout()
              }}
            />
          </div>
        </div>
      ) : null}
    </div>
  )
}

/**
 * Flashes the coin readout when the balance actually changes. The first settled
 * value only seeds the comparison, so arriving on a page never fakes a payout.
 */
function useBalanceChange(balance: number, isPending?: boolean) {
  const [changed, setChanged] = useState(false)
  const previous = useRef<number | null>(null)

  useEffect(() => {
    if (isPending) return

    if (previous.current === null) {
      previous.current = balance
      return
    }
    if (previous.current === balance) return

    previous.current = balance
    setChanged(true)
    const timer = window.setTimeout(() => setChanged(false), 700)
    return () => window.clearTimeout(timer)
  }, [balance, isPending])

  return changed
}

function AppWalletLink({ balance, isPending }: { balance: number; isPending?: boolean }) {
  const changed = useBalanceChange(balance, isPending)

  return (
    <NavLink
      to={SHOP_ROUTE}
      className={cn('app-wallet', changed && 'is-changed')}
      aria-label="Open shop"
      data-onboarding="wallet-balance"
    >
      <GitCoinIcon />
      <span>
        <strong>{formatBalance(balance, isPending)}</strong>
        <small>GitCoins</small>
      </span>
    </NavLink>
  )
}

function AppAccountCluster({ user }: { user: User | null }) {
  const navigate = useNavigate()
  const logout = useAppLogout()
  const wallet = useWalletSummary()
  const balance = wallet.data?.balance ?? 0

  return (
    <div className="app-account">
      <AudioControls className="app-audio-controls" buttonClassName="app-audio-control" />
      {user ? <AppWalletLink balance={balance} isPending={wallet.isPending} /> : null}
      {user ? <ProfileDropdown user={user} onLogout={logout} onNavigate={navigate} /> : null}
    </div>
  )
}

export function AppTopbar({ className }: { className?: string }) {
  const user = useAuthStore((state) => state.user)
  const scrolled = useScrolledPast()

  return (
    <header className={cn('app-topbar', className)} data-scrolled={scrolled ? 'true' : undefined}>
      <NavLink to="/home" aria-label="GIT it! home" className="app-brand">
        <span className="app-brand-sigil">
          <img src={gitLogoImage} alt="" />
        </span>
        <span className="app-brand-copy">
          <strong>GIT it!</strong>
          <small>Level up your Git</small>
        </span>
      </NavLink>

      <CurrentUserPrimaryNav navClassName="app-nav" linkClassName="app-nav-link" />

      <AppAccountCluster user={user} />
    </header>
  )
}


export function AppMobileNav() {
  const user = useAuthStore((state) => state.user)

  return (
    <PrimaryNav
      includeAdmin={Boolean(user?.is_staff)}
      navClassName={cn('app-mobile-nav', user?.is_staff && 'has-admin')}
      linkClassName="app-mobile-nav-link"
      activeClassName="is-active"
    />
  )
}
