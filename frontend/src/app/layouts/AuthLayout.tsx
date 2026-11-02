import { Outlet, useLocation } from 'react-router-dom'

import { BrandMark } from '@/features/auth/components/BrandMark'

const pageLabels: Record<string, string> = {
  '/login': 'Sign in',
  '/register': 'Create account',
  '/verify-email': 'Confirm your email',
  '/oauth/callback': 'Signing in',
  '/forgot-password': 'Password recovery',
}

export function AuthLayout() {
  const { pathname } = useLocation()
  const label = pathname.startsWith('/reset-password/') ? 'Choose a new password' : pageLabels[pathname] ?? 'Account'

  const isRegister = pathname === '/register'

  return (
    <main className="auth-shell">
      <div className="auth-reference-bg" aria-hidden="true" />
      <section className="auth-content" aria-label={label} data-page={isRegister ? 'register' : undefined}>
        <header className="auth-page-brand">
          <BrandMark size={isRegister ? 'sm' : 'lg'} />
          {!isRegister && <p>Learn Git through stories, battles, and a live repository graph.</p>}
        </header>
        <div className="auth-card auth-card--primary">
          <Outlet />
        </div>
      </section>
    </main>
  )
}
