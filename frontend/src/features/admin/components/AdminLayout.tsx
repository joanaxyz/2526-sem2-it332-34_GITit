import { BarChart3, ArrowLeft, Users } from 'lucide-react'
import { NavLink, Navigate, Outlet } from 'react-router-dom'

import { ADMIN_ROUTES, HOME_ROUTE } from '@/shared/navigation/routes'
import { useAuthStore } from '@/shared/auth/useAuth'
import { cn } from '@/shared/utils/cn'

const NAV_ITEMS = [
  { to: ADMIN_ROUTES.dashboard, label: 'KPI Overview', icon: BarChart3, end: true },
  { to: ADMIN_ROUTES.users,    label: 'Learners',     icon: Users,    end: false },
]

export function AdminLayout() {
  const user = useAuthStore((state) => state.user)
  if (!user) return <Navigate replace to="/login" />
  if (!user.is_staff) return <Navigate replace to={HOME_ROUTE} />

  return (
    <div className="adm-root">
      <header className="adm-topbar">
        <div className="adm-topbar-inner">
          <div className="adm-brand">
            <span className="adm-brand-eyebrow">Admin</span>
            <span className="adm-brand-name">GIT it!</span>
          </div>

          <nav className="adm-nav" aria-label="Admin navigation">
            {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) => cn('adm-nav-link', isActive && 'is-active')}
              >
                <Icon aria-hidden="true" />
                {label}
              </NavLink>
            ))}
          </nav>

          <NavLink to={HOME_ROUTE} className="adm-back-btn">
            <ArrowLeft aria-hidden="true" />
            Back to app
          </NavLink>
        </div>
      </header>

      <main className="adm-main">
        <div className="adm-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
