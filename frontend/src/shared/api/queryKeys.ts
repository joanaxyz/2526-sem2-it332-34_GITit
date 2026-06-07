import type { StoreyContentSection } from '@/features/challenges/types'

export const queryKeys = {
  authBootstrap: ['auth-bootstrap'] as const,
  dashboardSummary: ['dashboard-summary'] as const,
  foundations: ['foundations'] as const,
  storeys: ['storeys'] as const,
  storeyContent: (storeyId: number | null | undefined, section: StoreyContentSection) =>
    ['storey-content', storeyId, section] as const,
  commandFormPreview: (formId: number) => ['command-form-preview', formId] as const,
  challengeRun: (runId: number) => ['challenge-run', runId] as const,
  adventureRun: (runId: number) => ['adventure-run', runId] as const,
}

export const queryKeyRoots = {
  storeyContent: ['storey-content'] as const,
}
