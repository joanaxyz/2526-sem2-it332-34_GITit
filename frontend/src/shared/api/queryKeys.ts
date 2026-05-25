export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  lesson: (lessonId: number) => ['lesson', lessonId] as const,
  modules: ['modules'] as const,
  moduleScenarios: (moduleId: number | null | undefined) => ['module-scenarios', moduleId] as const,
  moduleScenariosSummary: (moduleIdsKey: string) => ['module-scenarios-summary', moduleIdsKey] as const,
  scenarioSession: (sessionId: number) => ['scenario-session', sessionId] as const,
  skillFocus: (slug: string) => ['skill-focus', slug] as const,
}

export const queryKeyRoots = {
  scenarioLists: ['module-scenarios'] as const,
  scenarioSummaries: ['module-scenarios-summary'] as const,
}
