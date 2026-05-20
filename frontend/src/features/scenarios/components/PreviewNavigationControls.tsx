import { ArrowLeft, ArrowRight, FastForward, Play } from 'lucide-react'

import { Button } from '@/shared/components/Button'

export function PreviewNavigationControls({
  canGoPrevious,
  canGoNext,
  isProceeding,
  onPrevious,
  onNext,
  onSkip,
  onStartPractice,
}: {
  canGoPrevious: boolean
  canGoNext: boolean
  isProceeding: boolean
  onPrevious: () => void
  onNext: () => void
  onSkip: () => void
  onStartPractice: () => void
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
      <div className="flex gap-2">
        <Button type="button" size="sm" variant="outline" disabled={!canGoPrevious || isProceeding} onClick={onPrevious}>
          <ArrowLeft data-icon="inline-start" />
          Previous
        </Button>
        <Button type="button" size="sm" variant="outline" disabled={!canGoNext || isProceeding} onClick={onNext}>
          Next
          <ArrowRight data-icon="inline-start" />
        </Button>
      </div>
      <div className="flex gap-2">
        <Button type="button" variant="ghost" disabled={isProceeding} onClick={onSkip}>
          <FastForward data-icon="inline-start" />
          Skip
        </Button>
        <Button type="button" disabled={isProceeding} onClick={onStartPractice}>
          <Play data-icon="inline-start" />
          {isProceeding ? 'Opening...' : 'Start scenario'}
        </Button>
      </div>
    </div>
  )
}
