import { BarChart3, ArrowLeft, Users } from 'lucide-react'
import { NavLink, Navigate, Outlet } from 'react-router-dom'

import { ADMIN_ROUTES, HOME_ROUTE } from '@/shared/navigation/routes'
import { useAuthStore } from '@/shared/auth/useAuth'
import { cn } from '@/shared/utils/cn'
import adminLogo from '@/assets/images/git-it-logo-new.lossless.webp'
import '@/styles/features/admin/sidebar.css'

const NAV_ITEMS = [
  { to: ADMIN_ROUTES.dashboard, label: 'KPI Overview', icon: BarChart3, end: true },
  { to: ADMIN_ROUTES.users,    label: 'Learners',     icon: Users,    end: false },
]

export function AdminLayout() {
  const user = useAuthStore((state) => state.user)
  if (!user) return <Navigate replace to="/login" />
  if (!user.is_staff) return <Navigate replace to={HOME_ROUTE} />

  return (
    <div className="adm-root adm-sidebar-layout">
      <aside className="adm-sidebar">
          <div className="adm-sidebar-brand">
            <img src={adminLogo} alt="GIT it!" />
            <span className="adm-brand-eyebrow">Admin portal</span>
          </div>

          <nav className="adm-sidebar-nav" aria-label="Admin navigation">
            {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) => cn('adm-sidebar-link', isActive && 'is-active')}
              >
                <Icon aria-hidden="true" />
                {label}
              </NavLink>
            ))}
          <NavLink to={HOME_ROUTE} className="adm-sidebar-link adm-sidebar-back">
            <ArrowLeft aria-hidden="true" />
            Back to app
          </NavLink>
          </nav>
      </aside>

      <main className="adm-main">
        <div className="adm-content">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
