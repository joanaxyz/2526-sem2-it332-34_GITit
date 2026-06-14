import { GitBranch, ShieldCheck, TerminalSquare } from 'lucide-react'
import { Link, Outlet, useLocation } from 'react-router-dom'

const loginHero = {
  title: 'Learn Git through repository state, not memorized answers.',
  description:
    'Learn with tomes, Command Adventures, Challenges, live DAG feedback, and consequence-safe command simulation.',
  terminal: (
    <>
      <span className="text-primary">student@git-it</span> ~/challenge $ git status
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
    'Track progress across Command Adventures and Challenges, experiment safely without touching a real shell, and grow confidence one command at a time.',
  terminal: (
    <>
      <span className="text-primary">you@git-it</span> ~/welcome $ git init
      <br />
      Initialized empty Git repository
      <br />
      Your level journey starts here.
    </>
  ),
}

const featureBadges = [
  {
    Icon: ShieldCheck,
    label: 'Consequence-safe runs',
    borderAccent: 'rgba(0,245,212,0.65)',
    border: 'rgba(0,245,212,0.22)',
    bg: 'rgba(0,245,212,0.06)',
    color: 'rgba(0,245,212,0.9)',
  },
  {
    Icon: TerminalSquare,
    label: 'State-based evaluation',
    borderAccent: 'rgba(0,180,216,0.65)',
    border: 'rgba(0,180,216,0.22)',
    bg: 'rgba(0,180,216,0.06)',
    color: 'rgba(0,180,216,0.9)',
  },
]

const panelShadow = '0 0 0 1px rgba(0,245,212,0.07), 0 22px 80px rgba(0,0,0,0.45)'

export function AuthLayout() {
  const location = useLocation()
  const isRegister = location.pathname === '/register'
  const hero = isRegister ? registerHero : loginHero

  return (
    <main className="relative grid min-h-dvh place-items-center px-4 py-4 sm:px-6 sm:py-6">
      {/* Page-level aurora accent */}
      <div className="pointer-events-none absolute -left-40 -top-40 h-96 w-96 rounded-full bg-aurora-cyan opacity-[0.05] blur-3xl" />

      <section className="grid w-full max-w-6xl grid-cols-[minmax(0,1.1fr)_minmax(320px,420px)] gap-4 max-md:grid-cols-1 md:min-h-[min(760px,90dvh)]">
        {/* -- Left: hero panel -- */}
        <div
          className="relative overflow-hidden rounded-lg border border-primary/15 bg-gradient-to-br from-secondary to-background p-6 max-md:hidden md:min-h-[min(760px,90dvh)]"
          style={{ boxShadow: panelShadow }}
        >
          {/* Aurora glow inside left panel */}
          <div className="pointer-events-none absolute -left-16 -top-16 h-72 w-72 rounded-full bg-aurora-cyan opacity-[0.06] blur-3xl" />

          <div className="relative z-10 flex h-full min-h-0 flex-col justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <span className="grid size-10 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary transition-all duration-200 hover:border-primary/60 hover:shadow-aurora-sm">
                <GitBranch />
              </span>
              <span className="text-xl font-extrabold tracking-tight">
                GIT <span className="text-primary">it!</span>
              </span>
            </Link>

            {/* Hero copy + badges */}
            <div className="max-w-lg">
              <h1 className="text-4xl font-extrabold leading-[1.08] tracking-tight">{hero.title}</h1>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">{hero.description}</p>

              {/* Feature badges - vertical, prominent */}
              <div className="mt-6 flex flex-col gap-2.5">
                {featureBadges.map(({ Icon, label, borderAccent, border, bg, color }) => (
                  <div
                    key={label}
                    className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-semibold"
                    style={{
                      background: bg,
                      border: `1px solid ${border}`,
                      borderLeft: `3px solid ${borderAccent}`,
                      color,
                    }}
                  >
                    <Icon className="size-4 shrink-0" />
                    {label}
                  </div>
                ))}
              </div>
            </div>

            {/* Terminal block */}
            <div
              className="overflow-hidden rounded-lg"
              style={{
                border: '1px solid rgba(0,245,212,0.22)',
                boxShadow: '0 0 24px rgba(0,245,212,0.06)',
              }}
            >
              {/* Window chrome */}
              <div
                className="flex items-center gap-1.5 bg-black/50 px-3 py-2"
                style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
              >
                <span className="size-2.5 rounded-full bg-[#FF5F57]" />
                <span className="size-2.5 rounded-full bg-[#FFBD2E]" />
                <span className="size-2.5 rounded-full bg-[#28CA41]" />
                <span className="ml-2 font-mono text-[10px] text-muted-foreground/40">bash</span>
              </div>
              {/* Terminal body */}
              <div className="bg-black/40 p-3 font-mono text-xs leading-6 text-accent">
                {hero.terminal}
                <span className="terminal-cursor" />
              </div>
            </div>
          </div>
        </div>

        {/* -- Right: form panel -- */}
        <div
          className="overflow-hidden rounded-lg border border-primary/15 bg-card p-5 sm:p-6 md:min-h-[min(760px,90dvh)]"
          style={{ boxShadow: panelShadow }}
        >
          <Outlet />
        </div>
      </section>
    </main>
  )
}
