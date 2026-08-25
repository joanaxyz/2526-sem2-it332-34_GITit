import { ArrowLeft } from 'lucide-react'
import { NavLink, Navigate, Outlet } from 'react-router-dom'

import { ADMIN_SECTIONS } from '@/features/admin/utils/adminSections'
import { useAuthStore } from '@/shared/auth/useAuth'
import { HOME_ROUTE } from '@/shared/navigation/routes'
import { cn } from '@/shared/utils/cn'

/** Staff-only console shell. Non-staff are redirected back to the app. */
export function AdminLayout() {
  const user = useAuthStore((state) => state.user)
  if (!user) return <Navigate replace to="/login" />
  if (!user.is_staff) return <Navigate replace to={HOME_ROUTE} />

  return (
    <div className="min-h-screen bg-background text-foreground" style={{ overflowX: 'clip' }}>
      <div className="mx-auto flex max-w-[1500px] gap-6 px-6 py-6 max-sm:px-3">
        <aside className="sticky top-6 hidden h-fit w-56 shrink-0 flex-col gap-1 md:flex">
          <div className="mb-3 px-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Admin</p>
            <p className="text-lg font-black text-primary">Observatory Console</p>
          </div>
          {ADMIN_SECTIONS.map(({ path, label, icon: Icon, end }) => (
            <NavLink
              key={path}
              to={path}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md border border-transparent px-3 py-2 text-sm font-medium transition',
                  isActive
                    ? 'border-primary/40 bg-secondary/70 text-primary'
                    : 'text-muted-foreground hover:border-border hover:bg-secondary/50 hover:text-foreground',
                )
              }
            >
              <Icon className="size-4" />
              {label}
            </NavLink>
          ))}
          <NavLink
            to={HOME_ROUTE}
            className="mt-4 flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground transition hover:text-foreground"
          >
            <ArrowLeft className="size-4" />
            Back to app
          </NavLink>
        </aside>

        {/* Mobile section tabs */}
        <div className="flex w-full flex-col gap-4">
          <nav className="app-scrollbar flex gap-2 overflow-x-auto md:hidden" aria-label="Admin sections">
            {ADMIN_SECTIONS.map(({ path, label, end }) => (
              <NavLink
                key={path}
                to={path}
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
