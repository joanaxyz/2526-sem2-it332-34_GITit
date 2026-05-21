import { BookOpen, Gauge, GitBranch, LogOut, PanelsTopLeft } from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { Button } from '@/shared/components/Button'
import { cn } from '@/shared/utils/cn'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: Gauge },
  { to: '/units', label: 'Modules', icon: BookOpen },
]

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
      <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex min-h-16 max-w-[1440px] items-center justify-between gap-3 px-6 py-3 max-sm:px-4">
          <div className="flex min-w-0 items-center gap-3">
            <span className="grid size-9 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
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
                    'inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm font-semibold text-muted-foreground transition hover:bg-secondary hover:text-foreground',
                    isActive && 'bg-secondary text-foreground',
                  )
                }
                to={item.to}
              >
                <item.icon className="size-4" />
                {item.label}
              </NavLink>
            ))}
          </nav>
          <div className="flex shrink-0 items-center gap-2">
            <div className="hidden items-center gap-2 text-sm text-muted-foreground md:flex">
              <PanelsTopLeft className="size-4" />
              {user?.student_id}
              {user && (
                <span className="text-foreground font-semibold">
                  {user.last_name}, {user.first_name}
                </span>
              )}
            </div>
            <Button variant="ghost" size="sm" onClick={logout}>
              <LogOut data-icon="inline-start" />
              <span className="max-sm:hidden">Logout</span>
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1440px] px-6 py-6 max-sm:px-4">
        <Outlet />
      </main>
    </div>
  )
}
