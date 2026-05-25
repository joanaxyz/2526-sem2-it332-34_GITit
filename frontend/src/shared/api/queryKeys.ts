export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  lesson: (lessonId: number) => ['lesson', lessonId] as const,
  lessonScenarios: (lessonId: number) => ['lesson-scenarios', lessonId] as const,
  modules: ['modules'] as const,
  moduleScenarios: (moduleId: number | null | undefined) => ['module-scenarios', moduleId] as const,
  moduleScenariosSummary: (moduleIdsKey: string) => ['module-scenarios-summary', moduleIdsKey] as const,
  scenarioSession: (sessionId: number) => ['scenario-session', sessionId] as const,
  skillFocus: (slug: string) => ['skill-focus', slug] as const,
  unitScenarios: (unitId: number) => ['unit-scenarios', unitId] as const,
  unitScenariosSummary: (unitIdsKey: string) => ['unit-scenarios-summary', unitIdsKey] as const,
}

export const queryKeyRoots = {
  scenarioLists: ['lesson-scenarios', 'module-scenarios', 'unit-scenarios'] as const,
  scenarioSummaries: ['module-scenarios-summary', 'unit-scenarios-summary'] as const,
}
