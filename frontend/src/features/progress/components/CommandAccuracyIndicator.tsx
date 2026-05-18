import type { RateMetric } from '@/features/dashboard/types'
import { KpiIndicatorCard } from './KpiIndicatorCard'

export function CommandAccuracyIndicator({ metric }: { metric: RateMetric }) {
  return <KpiIndicatorCard label="Command accuracy" metric={metric} />
}
