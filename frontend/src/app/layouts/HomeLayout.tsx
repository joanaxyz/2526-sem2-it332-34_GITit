import { useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  GitBranch,
  Lock,
  LogOut,
  Settings,
  Swords,
  Trophy,
  User,
  X,
  type LucideIcon,
} from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { WalletBadge } from '@/features/wallet/components/WalletBadge'
import { CursorGlow } from '@/shared/components/CursorGlow'
import { cn } from '@/shared/utils/cn'

const navItems = [
  { to: '/home', label: 'Home' },
  { to: '/tower', label: 'Tower' },
  { to: '/shop', label: 'Shop' },
]

function getInitials(username: string) {
  return (username?.slice(0, 2) || '??').toUpperCase()
}

function Avatar({
  initials,
  open = false,
  className = 'size-8',
}: {
  initials: string
  open?: boolean
  className?: string
}) {
  return (
    <span
      className={cn('grid shrink-0 place-items-center rounded-full text-xs font-bold', className)}
      style={{
        background: 'linear-gradient(135deg, #0c1e38 0%, #091428 100%)',
        border: '1.5px solid rgba(0,245,212,0.35)',
        borderColor: open ? 'rgba(0,245,212,0.65)' : 'rgba(0,245,212,0.35)',
        boxShadow: open ? '0 0 0 3px rgba(0,245,212,0.12)' : 'none',
        color: 'rgba(0,245,212,0.88)',
        transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
      }}
    >
      {initials}
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
        'flex w-full items-center gap-3 border-l-2 border-l-transparent px-4 py-2.5 text-sm transition-all duration-150',
        danger
          ? 'text-destructive hover:border-l-destructive/50 hover:bg-destructive/10'
          : 'text-muted-foreground hover:border-l-primary/60 hover:bg-secondary/60 hover:text-primary',
      )}
      onClick={onClick}
    >
      <Icon className="size-4 shrink-0" />
      {label}
    </button>
  )
}

function ProfileDropdown({
  user,
  onLogout,
}: {
  user: { username: string; email: string }
  onLogout: () => void
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  const initials = getInitials(user.username)
  const displayName = user.username || 'Adventurer'

  return (
    <div ref={ref} className="relative">
      {/* Trigger */}
      <button
        type="button"
        aria-expanded={open}
        aria-haspopup="true"
        className="flex items-center gap-2 rounded-md px-2 py-1.5 transition-all duration-200 hover:bg-secondary"
        onClick={() => setOpen((v) => !v)}
      >
        <Avatar initials={initials} open={open} />
        <span className="hidden text-sm font-semibold text-foreground md:inline">{displayName}</span>
        <ChevronDown
          className={cn(
            'size-3.5 text-muted-foreground transition-transform duration-200',
            open && 'rotate-180',
          )}
        />
      </button>

      {/* Dropdown panel */}
      {open && (
        <div
          className="dropdown-menu absolute right-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-xl border border-primary/15 bg-card"
          style={{
            boxShadow: '0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,245,212,0.18)',
          }}
        >
          {/* Identity header - avatar + name + email */}
          <div className="border-b border-border/40 px-4 py-3">
            <p className="truncate text-sm font-bold text-foreground">{displayName}</p>
            <p className="break-all text-xs leading-snug text-muted-foreground">{user.email}</p>
          </div>

          {/* Menu items */}
          <div className="py-1">
            <DropdownItem icon={User} label="Profile" onClick={() => setOpen(false)} />
            <DropdownItem icon={Settings} label="Settings" onClick={() => setOpen(false)} />
          </div>

          {/* Logout */}
          <div className="border-t border-border/40 py-1">
            <DropdownItem
              icon={LogOut}
              label="Logout"
              danger
              onClick={() => {
                setOpen(false)
                onLogout()
              }}
            />
          </div>
        </div>
      )}
    </div>
  )
}

function TowerHelpOverlay({ open, onClose }: { open: boolean; onClose: () => void }) {
  useEffect(() => {
    if (!open) return
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose, open])

  if (!open) return null

  const items = [
    { icon: Swords, copy: 'Clear each Command Adventure to unlock Challenges.' },
    { icon: Trophy, copy: 'Each challenge has Easy, Medium, and Hard levels.' },
    { icon: Lock, copy: 'Clear the storey levels to advance the tower.' },
    { icon: CheckCircle2, copy: 'Progress saves after every cleared level.' },
  ]

  return (
    <div className="tower-help-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        aria-modal="true"
        className="tower-help-overlay"
        role="dialog"
        aria-labelledby="tower-help-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="tower-help-title" className="text-xl font-black text-primary">How it works</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Climb the tower by clearing each storey&apos;s adventure and challenge set.
            </p>
          </div>
          <button
            type="button"
            className="tower-help-close"
            aria-label="Close tower help"
            onClick={onClose}
          >
            <X className="size-4" />
          </button>
        </div>
        <ul className="mt-6 grid gap-5">
          {items.map(({ icon: Icon, copy }) => (
            <li className="tower-help-item" key={copy}>
              <span className="tower-help-icon">
                <Icon className="size-5" />
              </span>
              <span>{copy}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export function HomeLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const user = useAuthStore((state) => state.user)
  const clearSession = useAuthStore((state) => state.clearSession)
  const [towerHelpOpen, setTowerHelpOpen] = useState(false)
  const isTowerPage =
    location.pathname.startsWith('/tower') && !location.pathname.includes('/editor')

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      queryClient.clear()
      clearSession()
      navigate('/login')
    }
  }

  return (
    <div className="min-h-screen" style={{ overflowX: 'clip' }}>
      <CursorGlow />
      {/* No header bar - only the wide launcher blade, with the logo and
          wallet/profile floating loose in the top corners (Halo-style). */}
      <header className="pointer-events-none sticky top-0 z-20 h-0">
        {/* Centered wide blade: \ Home | Tower / */}
        <div className="pointer-events-auto mx-auto w-fit">
          <div className="hub-nav-frame">
            <nav className="hub-nav" aria-label="Primary">
              {navItems.map((item, i) => (
                <span key={item.to} className="flex items-center gap-1.5">
                  {i > 0 && <span className="hub-nav-divider" aria-hidden="true" />}
                  <NavLink
                    className={({ isActive }) => cn('hub-nav-link', isActive && 'is-active')}
                    to={item.to}
                  >
                    {item.label}
                  </NavLink>
                </span>
              ))}
            </nav>
          </div>
        </div>

        {/* Floating logo chip - top left */}
        <NavLink
          to="/home"
          aria-label="GIT it! home"
          className="logo-badge pointer-events-auto absolute left-5 top-3 grid size-9 place-items-center rounded-md border border-primary/30 bg-background/55 text-primary backdrop-blur-md transition-all duration-200 hover:border-primary/60 max-sm:hidden"
        >
          <GitBranch />
        </NavLink>

        {/* Floating wallet + profile - top right */}
        <div className="pointer-events-auto absolute right-5 top-2.5 flex items-center gap-3 max-sm:right-3">
          {user && <WalletBadge />}
          {user && <ProfileDropdown user={user} onLogout={logout} />}
        </div>
      </header>
      <main className="mx-auto max-w-[1440px] px-6 py-6 max-sm:px-4">
        <Outlet />
      </main>

      {isTowerPage ? (
        <button
          type="button"
          className="tower-help-launcher"
          aria-label="Open tower guide"
          title="How tower works"
          onClick={() => setTowerHelpOpen(true)}
        >
          <CircleHelp className="size-5" />
        </button>
      ) : null}

      <TowerHelpOverlay open={towerHelpOpen} onClose={() => setTowerHelpOpen(false)} />
    </div>
  )
}
