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
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
      <div className="flex gap-2">
        <Button type="button" size="sm" variant="outline" disabled={isProceeding || !canGoPrevious} onClick={onPrevious}>
          <ArrowLeft data-icon="inline-start" />
          Previous
        </Button>
        <Button type="button" size="sm" variant="outline" disabled={isProceeding || !canGoNext} onClick={onNext}>
          Next
          <ArrowRight data-icon="inline-start" />
        </Button>
      </div>
      <div className="flex gap-2 border-l border-border pl-3">
        <Button type="button" disabled={isProceeding} onClick={onStartPractice}>
          <Play data-icon="inline-start" />
          {isProceeding ? 'Opening...' : startLabel}
        </Button>
      </div>
    </div>
  )
}
