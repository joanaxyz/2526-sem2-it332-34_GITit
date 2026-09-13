import { RotateCcw, Swords, Terminal } from 'lucide-react'

import { useModulePerformance } from '@/features/performance/hooks/useModulePerformance'
import { moduleColumnSeries } from '@/features/performance/utils/moduleColumns'
import type { RateMetric } from '@/features/performance/types'
import { MiniColumnChart } from '@/shared/components/charts/MiniColumnChart'

import type { HomeResultsModel } from './homeStatsModel'

/** Modules the practice metrics are reported for; the backend scopes to the same set. */
const REPORTED_MODULES = [1, 2, 3, 4] as const
const NO_ATTEMPTS = 'No attempts yet'

function formatNumber(value: number | null | undefined, fallback = 0) {
  return (typeof value === 'number' ? value : fallback).toLocaleString()
}

function formatPercent(value: number | null | undefined) {
  return typeof value === 'number' ? `${Math.round(value)}%` : '--'
}

function formatRetries(metric: RateMetric) {
  return metric.value == null ? '--' : metric.value.toFixed(2)
}

function runCount(metric: RateMetric, noun: string) {
  if (!metric.denominator) return NO_ATTEMPTS
  return `${formatNumber(metric.numerator)} of ${formatNumber(metric.denominator)} ${noun}`
}

type RecordTier = 'gold' | 'neutral' | 'empty'

function rateTier(metric: { value: number | null; denominator: number }): RecordTier {
  if (!metric.denominator || metric.value === null) return 'empty'
  return metric.value >= 100 ? 'gold' : 'neutral'
}

function accuracyTier(ready: boolean, value: number | null): RecordTier {
  if (!ready || value === null) return 'empty'
  return value >= 100 ? 'gold' : 'neutral'
}

/**
 * Per-module results, one small column chart per measure. They used to be twelve
 * stacked meters — three per module — which made "which module is my weakest?"
 * a scrolling comparison. Four columns side by side answer it at a glance, and
 * every value is printed on its own column, so nothing hides in a tooltip.
 */
function ModuleBreakdown() {
  const performance = useModulePerformance()

  if (performance.isPending) {
    return (
      <div className="home-overview-module-loading" role="status">
        <span className="sr-only">Loading module results</span>
        {REPORTED_MODULES.map((number) => (
          <i key={number} aria-hidden="true" />
        ))}
      </div>
    )
  }

  if (performance.isError || !performance.data) {
    return (
      <p className="home-overview-module-error" role="alert">
        Module results are unavailable right now. Your record above is still accurate.
      </p>
    )
  }

  const series = moduleColumnSeries(
    performance.data.modules.filter((module) =>
      REPORTED_MODULES.includes(module.number as (typeof REPORTED_MODULES)[number]),
    ),
  )

  if (!series.hasAnyData) {
    return (
      <p className="home-overview-module-empty">
        No main-story runs recorded yet. Clear a level and these four charts fill in.
      </p>
    )
  }

  return (
    <>
      <div className="home-overview-module-charts">
        <MiniColumnChart
          label={`Levels finished per module: ${series.levelsFinished.map((point) => `${point.caption} ${point.display}`).join(', ')}`}
          max={100}
          points={series.levelsFinished}
          title="Levels finished"
        />
        <MiniColumnChart
          label={`Hard levels finished per module: ${series.hardLevelsFinished.map((point) => `${point.caption} ${point.display}`).join(', ')}`}
          max={100}
          points={series.hardLevelsFinished}
          title="Hard levels finished"
        />
        <MiniColumnChart
          label={`Retries that worked per module: ${series.retriesThatWorked.map((point) => `${point.caption} ${point.display}`).join(', ')}`}
          max={100}
          points={series.retriesThatWorked}
          title="Retries that worked"
        />
        <MiniColumnChart
          label={`Retries per finish, per module: ${series.retriesPerFinish.map((point) => `${point.caption} ${point.display}`).join(', ')}`}
          points={series.retriesPerFinish}
          title="Retries per finish"
        />
      </div>
      <ul className="home-overview-module-key">
        {series.key.map((entry) => (
          <li key={entry.id}>
            <b>{entry.label}</b>
            {entry.title}
          </li>
        ))}
      </ul>
    </>
  )
}

export function HomeResultsPanel({ results }: { results: HomeResultsModel }) {
  return (
    <section className="home-overview-results-panel" aria-label="Run results" data-onboarding="overview-results">
      <header className="ref-panel-head">
        Your record <em>how the finishes went</em>
      </header>

      {/* Levels finished is absent on purpose: the citadel above already states it. */}
      <div className="home-overview-kpi-row">
        <div data-tier={rateTier(results.hardClearRate)}>
          <span className="home-overview-mini-sigil" aria-hidden="true"><Swords /></span>
          <strong>{formatPercent(results.hardClearRate.value)}</strong>
          <span>Hard levels finished</span>
          <small>{runCount(results.hardClearRate, 'hard runs')}</small>
        </div>
        <div data-tier={results.averageRetries.denominator ? 'neutral' : 'empty'}>
          <span className="home-overview-mini-sigil" aria-hidden="true"><RotateCcw /></span>
          <strong>{formatRetries(results.averageRetries)}</strong>
          <span>Retries per finish</span>
          <small>
            {results.averageRetries.denominator
              ? `Across ${formatNumber(results.averageRetries.denominator)} finished runs`
              : NO_ATTEMPTS}
          </small>
        </div>
        <div data-tier={accuracyTier(results.accuracyReady, results.accuracy)}>
          <span className="home-overview-mini-sigil" aria-hidden="true"><Terminal /></span>
          <strong>{results.accuracyReady ? formatPercent(results.accuracy) : '--'}</strong>
          <span>Commands accepted</span>
          <small>
            {results.accuracyReady
              ? `Across ${formatNumber(results.commandsRun)} commands`
              : 'Unlocks after 100 commands'}
          </small>
        </div>
      </div>

      <section className="home-overview-modules" aria-label="Main story modules 1 to 4">
        <header className="ref-panel-head">
          Main story <em>modules 1&ndash;4, practice runs only</em>
        </header>
        <ModuleBreakdown />
      </section>
    </section>
  )
}
