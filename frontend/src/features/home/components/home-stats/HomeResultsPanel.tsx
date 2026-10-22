import { RotateCcw } from 'lucide-react'

import { LearnerPerformanceInstrument } from '@/features/performance/components/LearnerPerformanceInstrument'
import { useModulePerformance } from '@/features/performance/hooks/useModulePerformance'

/** Progress owns its query locally so a failed record never hides activity. */
export function HomeResultsPanel() {
  const performance = useModulePerformance()

  return (
    <section className="home-overview-results-panel" aria-label="Practice record" data-onboarding="overview-results">
      <header className="performance-band-heading">
        <div>
          <h2>Your practice record</h2>
          <p>Select a measure to explore your modules.</p>
        </div>
        <span>Arcane Spire · Modules 1–4 · All time</span>
      </header>
      {performance.isPending ? (
        <div className="performance-loading" role="status">
          <span className="sr-only">Loading practice record</span>
          {Array.from({ length: 5 }, (_, index) => <i key={index} aria-hidden="true" />)}
        </div>
      ) : performance.isError || !performance.data ? (
        <div className="performance-error" role="alert">
          <p>Your practice record is unavailable right now. Your activity above is still available.</p>
          <button type="button" onClick={() => void performance.refetch()} disabled={performance.isFetching}>
            <RotateCcw aria-hidden="true" />{performance.isFetching ? 'Retrying…' : 'Retry'}
          </button>
        </div>
      ) : <LearnerPerformanceInstrument data={performance.data} />}
    </section>
  )
}
