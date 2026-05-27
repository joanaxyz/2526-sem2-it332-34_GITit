import { GitBranch, ShieldCheck, TerminalSquare } from 'lucide-react'
import { Link, Outlet, useLocation } from 'react-router-dom'

import { Badge } from '@/shared/components/Badge'

const loginHero = {
  title: 'Practice Git through repository state, not memorized answers.',
  description:
    'Learn with rich orientation lessons, scenario practice, live DAG feedback, and consequence-safe command simulation.',
  terminal: (
    <>
      <span className="text-primary">student@git-it</span> ~/scenario $ git status
      <br />
      On branch feature/login
      <br />
      Inspect first. Reason next.
    </>
  ),
}

const registerHero = {
  title: 'Create your account and start building real Git intuition.',
  description:
    'Track your progress across lessons and scenarios, practice safely without touching a real shell, and grow confidence one command at a time.',
  terminal: (
    <>
      <span className="text-primary">you@git-it</span> ~/welcome $ git init
      <br />
      Initialized empty Git repository
      <br />
      Your practice journey starts here.
    </>
  ),
}

export function AuthLayout() {
  const location = useLocation()
  const isRegister = location.pathname === '/register'
  const hero = isRegister ? registerHero : loginHero

  return (
    <main className="grid min-h-dvh place-items-center px-4 py-4 sm:px-6 sm:py-6">
      <section className="grid w-full max-w-6xl grid-cols-[minmax(0,1.1fr)_minmax(320px,420px)] gap-4 max-md:grid-cols-1 md:min-h-[min(760px,90dvh)]">
        <div className="relative overflow-hidden rounded-lg border border-border bg-gradient-to-br from-secondary to-background p-6 shadow-panel max-md:hidden md:min-h-[min(760px,90dvh)]">
          <div className="relative z-10 flex h-full min-h-0 flex-col justify-between">
            <Link to="/" className="flex items-center gap-3">
              <span className="grid size-10 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
                <GitBranch />
              </span>
              <span className="text-xl font-extrabold tracking-tight">
                GIT <span className="text-primary">it!</span>
              </span>
            </Link>
            <div className="max-w-lg">
              <h1 className="text-4xl font-extrabold leading-[1.08] tracking-tight">{hero.title}</h1>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">{hero.description}</p>
              <div className="mt-6 flex flex-wrap gap-2">
                <Badge variant="default">
                  <ShieldCheck className="size-3" />
                  No real Git execution
                </Badge>
                <Badge variant="blue">
                  <TerminalSquare className="size-3" />
                  State-based evaluation
                </Badge>
              </div>
            </div>
            <div className="rounded-lg border border-border bg-black/30 p-3 font-mono text-xs leading-6 text-accent">
              {hero.terminal}
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-border bg-card p-5 shadow-panel overflow-hidden sm:p-6 md:min-h-[min(760px,90dvh)]">
          <Outlet />
        </div>
      </section>
    </main>
  )
}
