import type { RateMetric } from '@/features/dashboard/types'
import { KpiIndicatorCard } from './KpiIndicatorCard'

export function HardLevelIndicator({ metric }: { metric: RateMetric }) {
  return <KpiIndicatorCard label="Hard-level completion" metric={metric} />
}
