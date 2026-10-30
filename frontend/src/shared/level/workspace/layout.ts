export const DAG_ZOOM_KEY = 'tier-workspace:dag-zoom-vertical'

export function stringList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []
}
