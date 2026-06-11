import { useQueryClient } from '@tanstack/react-query'
import {
  Castle,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Gauge,
  GitBranch,
  Lock,
  LogOut,
  Radar,
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
  { to: '/dashboard', label: 'Dashboard', icon: Gauge },
  { to: '/tower', label: 'Tower', icon: Castle },
  { to: '/stats', label: 'Stats', icon: Radar },
]

function getInitials(username: string) {
  return username.slice(0, 2).toUpperCase()
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
  const displayName = user.username

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
          {/* Identity header — avatar + name + email */}
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
    { icon: Swords, copy: 'Clear each Command Adventure to unlock GIT Challenged.' },
    { icon: Trophy, copy: 'Each challenge has Easy, Medium, and Hard levels.' },
    { icon: Lock, copy: 'Clear the storey levels to advance the tower.' },
    { icon: CheckCircle2, copy: 'Progress saves after every cleared practice.' },
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

export function DashboardLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const user = useAuthStore((state) => state.user)
  const clearSession = useAuthStore((state) => state.clearSession)
  const [towerHelpOpen, setTowerHelpOpen] = useState(false)
  const isTowerPage = location.pathname.startsWith('/tower')

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
    <div className="min-h-screen">
      <CursorGlow />
      <header
        className="sticky top-0 z-20 border-b border-primary/20 bg-background/60 backdrop-blur-md"
        style={{ boxShadow: '0 1px 10px rgba(0, 245, 212, 0.12), 0 1px 0 rgba(0, 245, 212, 0.18)' }}
      >
        <div className="mx-auto flex min-h-16 max-w-[1440px] items-center px-6 py-3 max-sm:px-4">
          {/* Left: logo + nav links grouped together */}
          <div className="flex items-center gap-6">
            <div className="flex min-w-0 items-center gap-3">
              <span className="logo-badge grid size-9 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary transition-all duration-200 hover:border-primary/60">
                <GitBranch />
              </span>
              <span className="whitespace-nowrap text-xl font-extrabold tracking-tight max-sm:text-lg">
                GIT <span className="text-primary">it!</span>
              </span>
            </div>
            <nav className="flex shrink-0 items-center gap-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  className={({ isActive }) =>
                    cn(
                      'inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold text-muted-foreground transition-all duration-200 hover:bg-secondary hover:text-foreground',
                      isActive &&
                      'bg-primary/10 text-primary shadow-[0_0_14px_rgba(0,245,212,0.28),inset_0_-2px_0_rgba(0,245,212,0.60)] ring-1 ring-inset ring-primary/30',
                    )
                  }
                  to={item.to}
                >
                  <item.icon className="size-4" />
                  <span className="max-sm:hidden">{item.label}</span>
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Right: GitCoin balance + profile dropdown */}
          <div className="ml-auto flex items-center gap-3">
            {user && <WalletBadge />}
            {user && <ProfileDropdown user={user} onLogout={logout} />}
          </div>
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
