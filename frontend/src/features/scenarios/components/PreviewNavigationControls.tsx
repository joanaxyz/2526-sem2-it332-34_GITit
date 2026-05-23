import { ArrowLeft, ArrowRight, Play } from 'lucide-react'

import { Button } from '@/shared/components/Button'

export function PreviewNavigationControls({
  canGoPrevious,
  canGoNext,
  isProceeding,
  startLabel = 'Start scenario',
  onPrevious,
  onNext,
  onStartPractice,
}: {
  canGoPrevious: boolean
  canGoNext: boolean
  isProceeding: boolean
  startLabel?: string
  onPrevious: () => void
  onNext: () => void
  onStartPractice: () => void
}) {
  const showStepControls = canGoPrevious || canGoNext

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
      {showStepControls ? (
        <div className="flex gap-2">
          {canGoPrevious ? (
            <Button type="button" size="sm" variant="outline" disabled={isProceeding} onClick={onPrevious}>
              <ArrowLeft data-icon="inline-start" />
              Previous
            </Button>
          ) : null}
          {canGoNext ? (
            <Button type="button" size="sm" variant="outline" disabled={isProceeding} onClick={onNext}>
              Next
              <ArrowRight data-icon="inline-start" />
            </Button>
          ) : null}
        </div>
      ) : (
        <div className="text-xs leading-5 text-muted-foreground">
          This preview is a short command warm-up, not a step-by-step answer path.
        </div>
      )}
      <div className="flex gap-2">
        <Button type="button" disabled={isProceeding} onClick={onStartPractice}>
          <Play data-icon="inline-start" />
          {isProceeding ? 'Opening...' : startLabel}
        </Button>
      </div>
    </div>
  )
}
