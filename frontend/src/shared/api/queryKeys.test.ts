import { describe, expect, it } from 'vitest'

import { queryKeys } from './queryKeys'

describe('queryKeys', () => {
  it('keeps stable keys for shared API state', () => {
    expect(queryKeys.modules).toEqual(['modules'])
    expect(queryKeys.dashboardSummary).toEqual(['dashboard-summary'])
    expect(queryKeys.moduleScenarios(12)).toEqual(['module-scenarios', 12])
    expect(queryKeys.moduleScenariosSummary('12,13')).toEqual(['module-scenarios-summary', '12,13'])
    expect(queryKeys.scenarioSession(99)).toEqual(['scenario-session', 99])
  })
})
