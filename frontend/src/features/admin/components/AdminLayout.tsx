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
    <div className="admin-shell">
      <div className="admin-shell-inner">
        <aside className="admin-sidebar">
          <div className="admin-sidebar-brand">
            <p>Admin</p>
            <strong>Observatory Console</strong>
          </div>
          {ADMIN_SECTIONS.map(({ path, label, icon: Icon, end }) => (
            <NavLink
              key={path}
              to={path}
              end={end}
              className={({ isActive }) => cn('admin-sidebar-link', isActive && 'is-active')}
            >
              <Icon className="size-4" />
              {label}
            </NavLink>
          ))}
          <NavLink to={HOME_ROUTE} className="admin-back-link">
            <ArrowLeft className="size-4" />
            Back to app
          </NavLink>
        </aside>

        {/* Mobile section tabs */}
        <div className="admin-content-wrap">
          <nav className="admin-mobile-nav" aria-label="Admin sections">
            {ADMIN_SECTIONS.map(({ path, label, end }) => (
              <NavLink
                key={path}
                to={path}
                end={end}
                className={({ isActive }) => cn('admin-mobile-link', isActive && 'is-active')}
              >
                {label}
              </NavLink>
            ))}
          </nav>
          <main className="admin-main">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  )
}
