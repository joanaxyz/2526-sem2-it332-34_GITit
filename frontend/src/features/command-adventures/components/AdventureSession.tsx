import { useState } from 'react'

import { CommandInput } from '@/shared/practice/components/CommandInput'
import { AdventureResult } from '@/features/command-adventures/components/AdventureResult'
import { useAdventureRun } from '@/features/command-adventures/hooks/useAdventureRun'
import type { AdventureRun } from '@/features/command-adventures/types'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { ProgressBar } from '@/shared/components/ProgressBar'

type TerminalLine = { command: string; output: string; solved: boolean }

export function AdventureSession({
  runId,
  onRestart,
}: {
  runId: number
  onRestart?: () => void
}) {
  const { query, submitCommand, useHint } = useAdventureRun(runId)
  const [lines, setLines] = useState<TerminalLine[]>([])

  if (query.isLoading) return <p className="p-8 text-sm text-muted-foreground">Loading adventure…</p>
  if (query.isError || !query.data)
    return <p className="p-8 text-sm text-red-400">Could not load this adventure run.</p>

  const run: AdventureRun = query.data
  const restart = onRestart ?? (() => {
    window.location.assign(`/command-adventures/${run.command_adventure.slug}`)
  })

  if (run.status !== 'started') {
    return <AdventureResult run={run} onRestart={restart} />
  }

  const attempt = run.current_attempt
  if (!attempt) return <p className="p-8 text-sm text-muted-foreground">Preparing next problem…</p>

  const progressValue = run.total_problems
    ? Math.round((run.progress.completed / run.total_problems) * 100)
    : 0
  const budget = attempt.command_budget
  const counted = attempt.counts.counted_command_count

  function handleSubmit(command: string) {
    submitCommand.mutate(command, {
      onSuccess: (response) => {
        setLines((prev) => [
          ...prev,
          { command, output: response.terminal_output || response.stdout || response.stderr, solved: response.solved },
        ])
      },
    })
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4 p-6">
      <header className="space-y-2">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>{run.command_adventure.title}</span>
          <span>
            Problem {attempt.order + 1} of {run.total_problems}
          </span>
        </div>
        <ProgressBar value={progressValue} glow segments={run.total_problems} />
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{attempt.problem.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {attempt.student_context.task ? (
            <p className="text-sm text-foreground">{attempt.student_context.task}</p>
          ) : (
            <p className="text-sm text-muted-foreground">{attempt.problem.summary}</p>
          )}
          <p className="text-xs text-muted-foreground">
            Commands used: {counted}/{budget.max_counted_commands} · Ideal: {budget.ideal_counted_commands} · Hints:{' '}
            {attempt.counts.hint_count}
          </p>
        </CardContent>
      </Card>

      <div className="overflow-hidden rounded-lg border border-border bg-[#0d1017]">
        <div className="max-h-64 min-h-[6rem] space-y-2 overflow-y-auto p-3 font-mono text-xs">
          {lines.length === 0 ? (
            <p className="text-muted-foreground/60">Run a git command to begin.</p>
          ) : (
            lines.map((line, index) => (
              <div key={index}>
                <div className="text-emerald-400">$ {line.command}</div>
                {line.output ? <pre className="whitespace-pre-wrap text-foreground/85">{line.output}</pre> : null}
              </div>
            ))
          )}
        </div>
        <CommandInput
          onSubmit={handleSubmit}
          processing={submitCommand.isPending}
          disabled={submitCommand.isPending}
        />
      </div>

      {useHint.data?.hint ? (
        <Card className="border-amber-500/30 bg-amber-500/[0.06]">
          <CardContent className="py-3 text-sm text-amber-200/90">
            <span className="font-semibold">Hint {useHint.data.hint_number}:</span> {useHint.data.hint}
          </CardContent>
        </Card>
      ) : null}

      <div className="flex justify-end">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => useHint.mutate()}
          disabled={useHint.isPending}
        >
          Use a hint
        </Button>
      </div>
    </div>
  )
}
