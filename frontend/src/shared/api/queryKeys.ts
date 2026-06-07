import type { TowerContentSection } from '@/features/scenarios/types'

export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  foundations: ['foundations'] as const,
  storeys: ['storeys'] as const,
  towers: ['storeys'] as const,
  modules: ['storeys'] as const,
  storeyContent: (storeyId: number | null | undefined, section: TowerContentSection) =>
    ['storey-content', storeyId, section] as const,
  moduleContent: (moduleId: number | null | undefined, section: TowerContentSection) =>
    ['storey-content', moduleId, section] as const,
  commandUsagePreview: (usageId: number) => ['command-usage-preview', usageId] as const,
  practiceSession: (sessionId: number) => ['practice-session', sessionId] as const,
}

export const queryKeyRoots = {
  storeyContent: ['storey-content'] as const,
  moduleContent: ['storey-content'] as const,
}
