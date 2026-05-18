import { CheckCircle2, RotateCcw, XCircle } from 'lucide-react'

import { scenariosApi } from '@/features/scenarios/api/scenariosApi'
import type { ScenarioSession } from '@/features/practice/types'
import { Button } from '@/shared/components/Button'
import { Card } from '@/shared/components/Card'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { syncScenarioSessionInCache } from '@/features/scenarios/utils/scenarioCache'

export function SessionOutcomeBanner({ session }: { session: ScenarioSession }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const retryMutation = useMutation({
    mutationFn: () => scenariosApi.retrySession(session.id),
    onSuccess: (next) => {
      syncScenarioSessionInCache(queryClient, next)
      navigate(`/practice/${next.id}`)
    },
  })

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
        {!completed && !session.review_mode ? (
          <Button type="button" onClick={() => retryMutation.mutate()}>
            Retry changed variant
          </Button>
        ) : null}
      </div>
    </Card>
  )
}
