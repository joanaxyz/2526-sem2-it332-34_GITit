import { Lightbulb } from 'lucide-react'

import { Button } from '@/shared/components/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/components/Card'
import { cn } from '@/shared/utils/cn'

export type RevealedHint = { number: number; text: string }

/**
 * Hint surface for the adventure workspace. Mirrors the challenge
 * {@link import('@/shared/level/components/ContextualFeedbackPanel').ContextualFeedbackPanel}
 * design — a quiet card with an icon-led title and a single body line — so the
 * two level modes feel like one product.
 */
export function AdventureHintPanel({
  hint,
  hintCount,
  isRevealing,
  onReveal,
  className,
}: {
  hint: RevealedHint | null
  hintCount: number
  isRevealing: boolean
  onReveal: () => void
  className?: string
}) {
  return (
    <Card className={cn('w-full min-w-0 shadow-none', className)}>
      <CardHeader className="flex-row items-center justify-between gap-2 p-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          <Lightbulb className="size-5 text-primary" />
          Hints
          {hintCount > 0 ? (
            <span className="font-mono text-[11px] font-normal text-muted-foreground">used {hintCount}</span>
          ) : null}
        </CardTitle>
        <Button type="button" variant="secondary" size="sm" onClick={onReveal} disabled={isRevealing}>
          {isRevealing ? 'Revealing…' : hint ? 'Next hint' : 'Reveal hint'}
        </Button>
      </CardHeader>
      <CardContent className="p-3 pt-0">
        {hint ? (
          <p className="text-sm leading-6 text-foreground">
            <span className="font-semibold text-primary">Hint {hint.number}.</span> {hint.text}
          </p>
        ) : (
          <p className="text-sm leading-6 text-muted-foreground">
            Stuck? Reveal a hint — using one lowers your independence score for this level.
          </p>
        )}
      </CardContent>
    </Card>
  )
}
