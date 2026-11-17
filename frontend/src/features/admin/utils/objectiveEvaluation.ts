import { EMPTY_RATE, getModuleRate, type Rate, type Status, type SoMetric, type SpecificObjective } from './kpiCatalogue'
import type { PerformanceModule } from '@/features/performance/types'
import { metricTargetStatus } from '@/features/performance/utils/performanceKpis'

// A multi-metric SO misses if any metric misses, is met only when every metric
// is met, and otherwise has no verdict yet.
export function combinedStatus(statuses: Status[]): Status {
  if (statuses.includes('miss')) return 'miss'
  if (statuses.length > 0 && statuses.every(st => st === 'met')) return 'met'
  return 'none'
}

// CAR is measured per SO (from the SO-to-level mapping); every other KPI is
// measured per module.
export type SoData = { module: PerformanceModule | undefined; objectives: Record<string, Rate> }

export function soMetricRate(metric: SoMetric, so: SpecificObjective, data: SoData): Rate {
  if (metric.kpi === 'car') return data.objectives[so.id] ?? EMPTY_RATE
  return data.module ? getModuleRate(data.module, metric.kpi) : EMPTY_RATE
}

export function soStatus(so: SpecificObjective, data: SoData): Status {
  return combinedStatus(so.metrics.map(m => metricTargetStatus(soMetricRate(m, so, data), m.target, m.up)))
}

