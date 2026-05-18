import { GitBranch, ShieldCheck, TerminalSquare } from 'lucide-react'
import { Link, Outlet } from 'react-router-dom'

import { Badge } from '@/shared/components/Badge'

export function AuthLayout() {
  return (
    <main className="grid min-h-screen place-items-center px-6 py-8">
      <section className="grid w-full max-w-6xl grid-cols-[minmax(0,1.1fr)_minmax(340px,420px)] gap-4 max-lg:grid-cols-1">
        <div className="relative overflow-hidden rounded-lg border border-border bg-gradient-to-br from-secondary to-background p-10 shadow-panel">
          <div className="relative z-10 flex min-h-[34rem] flex-col justify-between">
            <Link to="/" className="flex items-center gap-3">
              <span className="grid size-10 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
                <GitBranch />
              </span>
              <span className="text-2xl font-extrabold tracking-tight">
                GIT <span className="text-primary">it!</span>
              </span>
            </Link>
            <div className="max-w-xl">
              <h1 className="text-5xl font-extrabold leading-[1.03] tracking-tight max-md:text-4xl">
                Practice Git through repository state, not memorized answers.
              </h1>
              <p className="mt-5 text-base leading-7 text-muted-foreground">
                Learn with rich orientation lessons, scenario practice, live DAG feedback, and consequence-safe command simulation.
              </p>
              <div className="mt-8 flex flex-wrap gap-2">
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
            <div className="rounded-lg border border-border bg-black/30 p-4 font-mono text-sm leading-7 text-accent">
              <span className="text-primary">student@git-it</span> ~/scenario $ git status
              <br />
              On branch feature/login
              <br />
              Inspect first. Reason next.
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-border bg-card p-8 shadow-panel">
          <Outlet />
        </div>
      </section>
    </main>
  )
}
