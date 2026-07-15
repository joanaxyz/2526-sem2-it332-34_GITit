import {
  BarChart3,
  BookText,
  Boxes,
  Coins,
  LayoutDashboard,
  Layers,
  Settings,
  ShieldAlert,
  Store,
  Users,
  ArrowLeft,
} from 'lucide-react'
import { NavLink, Navigate, Outlet } from 'react-router-dom'

import { useAuthStore } from '@/shared/auth/useAuth'
import { cn } from '@/shared/utils/cn'

const sections = [
  { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/admin/users', label: 'Users', icon: Users },
  { to: '/admin/economy', label: 'Economy', icon: Coins },
  { to: '/admin/assets', label: 'Assets', icon: Boxes },
  { to: '/admin/shop', label: 'Shop', icon: Store },
  { to: '/admin/curriculum', label: 'Curriculum', icon: Layers },
  { to: '/admin/content', label: 'Content', icon: BookText },
  { to: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/admin/moderation', label: 'Moderation', icon: ShieldAlert },
  { to: '/admin/settings', label: 'Settings', icon: Settings },
]

/** Staff-only console shell. Non-staff are redirected back to the app. */
export function AdminLayout() {
  const user = useAuthStore((state) => state.user)
  if (!user) return <Navigate replace to="/login" />
  if (!user.is_staff) return <Navigate replace to="/home" />

  return (
    <div className="min-h-screen bg-background text-foreground" style={{ overflowX: 'clip' }}>
      <div className="mx-auto flex max-w-[1500px] gap-6 px-6 py-6 max-sm:px-3">
        <aside className="sticky top-6 hidden h-fit w-56 shrink-0 flex-col gap-1 md:flex">
          <div className="mb-3 px-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Admin</p>
            <p className="text-lg font-black text-primary">Observatory Console</p>
          </div>
          {sections.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md border-l-2 border-l-transparent px-3 py-2 text-sm font-medium transition',
                  isActive
                    ? 'border-l-primary bg-secondary/70 text-primary'
                    : 'text-muted-foreground hover:bg-secondary/50 hover:text-foreground',
                )
              }
            >
              <Icon className="size-4" />
              {label}
            </NavLink>
          ))}
          <NavLink
            to="/home"
            className="mt-4 flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to app
          </NavLink>
        </aside>

        {/* Mobile section tabs */}
        <div className="flex w-full flex-col gap-4">
          <nav className="app-scrollbar flex gap-2 overflow-x-auto md:hidden" aria-label="Admin sections">
            {sections.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  cn(
                    'whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-semibold transition',
                    isActive ? 'bg-primary/15 text-primary' : 'bg-secondary/50 text-muted-foreground',
                  )
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <main className="min-w-0 flex-1">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
