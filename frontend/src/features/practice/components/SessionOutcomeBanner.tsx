import { CheckCircle2, RotateCcw, XCircle } from 'lucide-react'

import type { ScenarioSession } from '@/features/practice/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'

export function SessionOutcomeBanner({
  session,
  isRetrying = false,
  onRetry,
}: {
  session: ScenarioSession
  isRetrying?: boolean
  onRetry?: () => void
}) {
  if (session.status === 'started') return null
  const completed = session.status === 'completed'
  return (
    <Card className="border-primary/30 bg-primary/10 p-3 shadow-none">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          {completed ? <CheckCircle2 className="size-5 text-primary" /> : session.status === 'failed' ? <XCircle className="size-5 text-destructive" /> : <RotateCcw className="size-5 text-amber-300" />}
          <div>
            <div className="font-semibold capitalize">{session.status}</div>
            <p className="mt-1 text-sm text-muted-foreground">
              {completed
                ? 'Completion was logged without revealing command answers.'
                : 'The next retry uses a structurally different variant when available.'}
            </p>
          </div>
        </div>
        {!completed && !session.review_mode && onRetry ? (
          <Button type="button" disabled={isRetrying} onClick={onRetry}>
            {isRetrying ? 'Starting retry' : 'Retry changed variant'}
          </Button>
        ) : null}
      </div>
    </Card>
  )
}
