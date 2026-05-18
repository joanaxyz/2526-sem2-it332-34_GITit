import { ArrowLeft, GitBranch } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { ScenarioSession } from '@/features/practice/types'
import { Badge } from '@/shared/components/Badge'
import { Button } from '@/shared/components/Button'

export function ScenarioStatusHeader({ session }: { session: ScenarioSession }) {
  return (
    <header className="flex h-12 items-center justify-between gap-3 border-b border-border bg-background px-3">
      <div className="flex min-w-0 items-center gap-3">
        <Button asChild variant="ghost" size="sm">
          <Link to="/units">
            <ArrowLeft data-icon="inline-start" />
            Back
          </Link>
        </Button>
        <GitBranch className="size-5 text-primary" />
        <span className="truncate font-mono text-xs text-muted-foreground">
          Unit {session.unit.number} / {session.scenario.focus}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <Badge variant={session.status === 'completed' ? 'default' : session.status === 'failed' ? 'destructive' : 'blue'}>
          {session.status}
        </Badge>
        <Badge variant="outline">{session.variant.label}</Badge>
      </div>
    </header>
  )
}
