import { BarChart2, BookOpen, ChevronDown, Gauge, GitBranch, LogOut, Settings, User, type LucideIcon } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { CursorGlow } from '@/shared/components/CursorGlow'
import { cn } from '@/shared/utils/cn'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: Gauge },
  { to: '/modules', label: 'Modules', icon: BookOpen },
  { to: '/performance', label: 'Performance', icon: BarChart2 },
]

function getInitials(firstName: string, lastName: string) {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
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
  user: { first_name: string; last_name: string; student_id: string; email: string }
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

  const initials = getInitials(user.first_name, user.last_name)
  const fullName = `${user.last_name}, ${user.first_name}`

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
        <span className="hidden text-sm font-semibold text-foreground md:inline">{fullName}</span>
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
            <p className="truncate text-sm font-bold text-foreground">{fullName}</p>
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

export function DashboardLayout() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const clearSession = useAuthStore((state) => state.clearSession)

  async function logout() {
    try {
      await authApi.logout()
    } finally {
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
              <span className="grid size-9 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary transition-all duration-200 hover:border-primary/60 hover:shadow-[0_0_14px_rgba(0,245,212,0.55)]">
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
                        'bg-primary/10 text-primary ring-1 ring-inset ring-primary/30 shadow-[0_0_10px_rgba(0,245,212,0.2)]',
                    )
                  }
                  to={item.to}
                >
                  <item.icon className="size-4" />
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Right: profile dropdown */}
          <div className="ml-auto">
            {user && <ProfileDropdown user={user} onLogout={logout} />}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1440px] px-6 py-6 max-sm:px-4">
        <Outlet />
      </main>
    </div>
  )
}
