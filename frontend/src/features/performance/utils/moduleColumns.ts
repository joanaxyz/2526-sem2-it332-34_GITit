import type { PerformanceModule, RateMetric } from '@/features/performance/types'
import type { ColumnPoint } from '@/shared/components/charts/MiniColumnChart'

const NO_ATTEMPTS = 'No attempts yet'

function formatNumber(value: number) {
  return value.toLocaleString()
}

function caption(module: PerformanceModule) {
  const untitled = module.title.toLowerCase() === `module ${module.number}`
  return untitled ? `Module ${module.number}` : `Module ${module.number} - ${module.title}`
}

function rateColumn(module: PerformanceModule, metric: RateMetric, noun: string): ColumnPoint {
  const measured = metric.denominator > 0 && metric.value !== null
  return {
    key: `module-${module.number}`,
    label: `M${module.number}`,
    caption: caption(module),
    value: measured ? Math.round(metric.value as number) : null,
    display: measured ? `${Math.round(metric.value as number)}%` : '--',
    detail: measured
      ? `${formatNumber(metric.numerator)} of ${formatNumber(metric.denominator)} ${noun}`
      : NO_ATTEMPTS,
  }
}

function retryColumn(module: PerformanceModule): ColumnPoint {
  const metric = module.arc
  const measured = metric.denominator > 0 && metric.value !== null
  return {
    key: `module-${module.number}`,
    label: `M${module.number}`,
    caption: caption(module),
    value: measured ? (metric.value as number) : null,
    display: measured ? (metric.value as number).toFixed(2) : '--',
    detail: measured ? `Across ${formatNumber(metric.denominator)} finished runs` : NO_ATTEMPTS,
  }
}

/**
 * One column series per measure, because the four measures do not share a unit:
 * three are percentages of different denominators and the fourth is a count per
 * finish. Plotted together they would need a second y-axis, which would make the
 * comparison up.
 */
export function moduleColumnSeries(modules: PerformanceModule[]) {
  return {
    /** False for a fresh account: four empty plots say less than one sentence. */
    hasAnyData: modules.some((module) =>
      [module.scr, module.hlcr, module.rtr, module.arc].some((metric) => metric.denominator > 0),
    ),
    levelsFinished: modules.map((module) => rateColumn(module, module.scr, 'runs')),
    hardLevelsFinished: modules.map((module) => rateColumn(module, module.hlcr, 'hard runs')),
    retriesThatWorked: modules.map((module) => rateColumn(module, module.rtr, 'retries')),
    retriesPerFinish: modules.map(retryColumn),
    /** Expands the "M1" ticks: the axis stays short, the names stay visible. */
    key: modules.map((module) => ({ id: module.number, label: `M${module.number}`, title: caption(module) })),
  }
}
