import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'
import type { AdventureRun } from '@/features/command-adventures/types'

function bandLabel(score: number): string {
  if (score < 70) return 'Failed'
  if (score < 85) return 'Passed'
  if (score < 95) return 'Strong pass'
  return 'Mastered'
}

export function AdventureResult({ run, onRestart }: { run: AdventureRun; onRestart: () => void }) {
  const masteryPercent = Math.round(run.mastery_progress_gained * 100)
  return (
    <Card className="mx-auto mt-10 w-full max-w-2xl">
      <CardHeader>
        <CardTitle>
          {run.status === 'completed' ? 'Adventure complete' : 'Adventure ended'} — {run.command_adventure.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div>
          <div className="mb-1 flex justify-between text-sm text-muted-foreground">
            <span>Mastery gained</span>
            <span>{masteryPercent}%</span>
          </div>
          <ProgressBar value={masteryPercent} fillAnimate glow />
        </div>
        <p className="text-sm text-muted-foreground">
          Overall score <span className="font-semibold text-foreground">{run.total_score}</span> · Status{' '}
          <span className="font-semibold text-foreground">{run.status}</span>
        </p>
        <ul className="divide-y divide-border rounded-md border border-border">
          {run.results.map((result) => (
            <li key={result.id} className="flex items-center justify-between gap-3 px-4 py-2.5 text-sm">
              <span className="text-muted-foreground">Problem {result.order + 1}</span>
              <span className="font-mono">{result.final_score}</span>
              <span
                className={
                  result.status === 'completed' ? 'text-emerald-400' : 'text-red-400'
                }
              >
                {bandLabel(result.final_score)}
              </span>
            </li>
          ))}
        </ul>
        <Button onClick={onRestart} className="w-full">
          Try again
        </Button>
      </CardContent>
    </Card>
  )
}
