import type { TowerContentSection } from '@/features/scenarios/types'

export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  foundations: ['foundations'] as const,
  towers: ['towers'] as const,
  modules: ['towers'] as const,
  towerContent: (towerId: number | null | undefined, section: TowerContentSection) =>
    ['tower-content', towerId, section] as const,
  moduleContent: (moduleId: number | null | undefined, section: TowerContentSection) =>
    ['tower-content', moduleId, section] as const,
  commandUsagePreview: (usageId: number) => ['command-usage-preview', usageId] as const,
  practiceSession: (sessionId: number) => ['practice-session', sessionId] as const,
}

export const queryKeyRoots = {
  towerContent: ['tower-content'] as const,
  moduleContent: ['tower-content'] as const,
}
