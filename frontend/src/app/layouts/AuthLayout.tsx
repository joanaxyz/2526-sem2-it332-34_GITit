import { ShieldCheck, TerminalSquare, Trophy, type LucideIcon } from 'lucide-react'
import { Outlet, useLocation } from 'react-router-dom'

import { AuthSky } from '@/features/auth/components/AuthSky'
import { BrandMark } from '@/features/auth/components/BrandMark'

type Hero = {
  title: string
  description: string
}

const HEROES: Record<'login' | 'register' | 'forgot', Hero> = {
  login: {
    title: 'Learn Git through repository state, not memorized answers.',
    description:
      'Reason about the repo, run commands in a consequence-safe shell, and watch the DAG prove you right.',
  },
  register: {
    title: 'Start building real Git intuition.',
    description:
      'Climb the tower one cleared command at a time. Experiment safely, never touch a real shell, and let progress feel earned.',
  },
  forgot: {
    title: 'Every climber loses the thread sometimes.',
    description: "Locked out? Here's the fastest way back onto the tower.",
  },
}

// One source of truth for the value props — they used to be duplicated between
// the left panel and an in-form list (and "consequence-safe runs" appeared
// twice on the login screen).
const CREDENTIALS: { Icon: LucideIcon; label: string }[] = [
  { Icon: ShieldCheck, label: 'Consequence-safe runs — never touch a real repo' },
  { Icon: TerminalSquare, label: 'A live DAG that answers every command' },
  { Icon: Trophy, label: 'Progress that carries across every tower' },
]

function heroFor(pathname: string): Hero {
  if (pathname === '/register') return HEROES.register
  if (pathname === '/forgot-password') return HEROES.forgot
  return HEROES.login
}

export function AuthLayout() {
  const { pathname } = useLocation()
  const hero = heroFor(pathname)

  return (
    <main className="auth-shell">
      <AuthSky />

      <div className="auth-content">
        {/* Hero column — open over the sky, no container (desktop only). */}
        <section className="auth-hero max-lg:hidden">
          <BrandMark size="lg" />

          <div className="auth-hero-copy">
            <h1 className="auth-hero-title text-pretty">{hero.title}</h1>
            <p className="auth-hero-desc">{hero.description}</p>
          </div>

          <ul className="auth-creds">
            {CREDENTIALS.map(({ Icon, label }) => (
              <li key={label} className="auth-cred">
                <Icon className="auth-cred-icon" aria-hidden="true" />
                <span>{label}</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Form column — the glass plaque. */}
        <section className="auth-card">
          {/* Mobile-only brand header so phone users keep identity + an exit. */}
          <div className="mb-5 lg:hidden">
            <BrandMark size="sm" />
          </div>
          <Outlet />
        </section>
      </div>
    </main>
  )
}
