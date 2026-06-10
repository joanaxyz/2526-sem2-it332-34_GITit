import { Castle, DoorOpen, Sparkles } from 'lucide-react'

import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'
import type { AdventureRun } from '@/features/command-adventures/types'

export function AdventureResult({
  run,
  onRestart,
  onBackToTower,
}: {
  run: AdventureRun
  onRestart: () => void
  onBackToTower?: () => void
}) {
  const { session_score, pass_bar, total_achievable, commands_mastered, total_commands, passed, commands } =
    run.mastery
  const scorePercent = Math.round((session_score / Math.max(total_achievable, 1)) * 100)

  return (
    <Card className="mx-auto mt-10 w-full max-w-2xl">
      <CardHeader>
        <CardTitle>
          {passed ? 'Adventure passed' : 'Adventure ended'} — {run.command_adventure.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {passed ? (
          <div className="flex items-center gap-2 rounded-md border border-accent/40 bg-accent/10 px-3 py-2 text-sm text-accent">
            <DoorOpen className="size-4" />
            <span className="font-semibold">Challenge unlocked</span>
            <Sparkles className="size-3.5" />
          </div>
        ) : null}
        <div>
          <div className="mb-1 flex justify-between text-sm text-muted-foreground">
            <span>Session score</span>
            <span>
              <span className="font-semibold text-foreground">{session_score}</span> / {total_achievable} pts
            </span>
          </div>
          <ProgressBar value={scorePercent} fillAnimate glow />
          <p className="mt-1 text-xs text-muted-foreground">
            Pass bar {pass_bar} · {commands_mastered}/{total_commands} commands mastered
          </p>
        </div>
        <ul className="divide-y divide-border rounded-md border border-border">
          {commands.map((command) => (
            <li key={command.slug} className="flex items-center justify-between gap-3 px-4 py-2.5 text-sm">
              <span className="text-muted-foreground">{command.title}</span>
              <span className="font-mono">
                {command.strength}/{command.mastered_bar}
              </span>
              <span
                className={
                  command.mastered
                    ? 'text-emerald-400'
                    : command.introduced
                      ? 'text-amber-400'
                      : 'text-muted-foreground'
                }
              >
                {command.mastered ? 'Mastered' : command.introduced ? 'In progress' : 'Untried'}
              </span>
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-2 sm:flex-row">
          {onBackToTower ? (
            <Button variant="secondary" onClick={onBackToTower} className="w-full">
              <Castle data-icon="inline-start" />
              Back to Tower
            </Button>
          ) : null}
          <Button onClick={onRestart} className="w-full">
            {passed ? 'Practice again' : 'Try again'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
