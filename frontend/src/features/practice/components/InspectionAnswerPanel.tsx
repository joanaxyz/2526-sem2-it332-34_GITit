import { ClipboardCheck, Send } from 'lucide-react'
import { useMemo, useState } from 'react'

import type { ScenarioSession } from '@/features/practice/types'
import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'

export function InspectionAnswerPanel({
  disabled,
  isSubmitting,
  session,
  onSubmit,
}: {
  disabled?: boolean
  isSubmitting?: boolean
  session: ScenarioSession
  onSubmit: (answer: Record<string, unknown>) => void
}) {
  const initialValue = useMemo(
    () => (session.inspection_answer ? JSON.stringify(session.inspection_answer, null, 2) : '{\n  \n}'),
    [session.inspection_answer],
  )
  const [value, setValue] = useState(initialValue)
  const [error, setError] = useState('')

  function submit() {
    try {
      const parsed = JSON.parse(value)
      if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
        setError('Submit a JSON object.')
        return
      }
      setError('')
      onSubmit(parsed as Record<string, unknown>)
    } catch {
      setError('Check the JSON syntax.')
    }
  }

  return (
    <Card className="shadow-none">
      <CardHeader className="p-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <ClipboardCheck className="size-4 text-primary" />
          Inspection Answer
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 p-3 pt-0">
        <textarea
          className="min-h-32 w-full resize-none rounded-md border border-border bg-background/60 p-2 font-mono text-xs leading-5 text-foreground outline-none focus-visible:ring-2 focus-visible:ring-ring"
          disabled={disabled || isSubmitting}
          spellCheck={false}
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
        {error ? <p className="text-xs font-medium text-destructive">{error}</p> : null}
        <Button className="w-full" disabled={disabled || isSubmitting} size="sm" type="button" onClick={submit}>
          <Send className="size-3.5" />
          Submit Answer
        </Button>
      </CardContent>
    </Card>
  )
}
