import type { ModuleContentSection } from '@/features/scenarios/types'

export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  foundations: ['foundations'] as const,
  modules: ['modules'] as const,
  moduleContent: (moduleId: number | null | undefined, section: ModuleContentSection) =>
    ['module-content', moduleId, section] as const,
  commandUsagePreview: (usageId: number) => ['command-usage-preview', usageId] as const,
  practiceSession: (sessionId: number) => ['practice-session', sessionId] as const,
}

export const queryKeyRoots = {
  moduleContent: ['module-content'] as const,
}
