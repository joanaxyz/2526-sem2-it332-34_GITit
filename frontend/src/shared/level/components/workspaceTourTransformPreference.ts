import type {
  WorkspaceTourPane as Pane,
  WorkspaceTourPosition as Position,
  WorkspaceTourSize as Size,
} from './gameplayWorkspaceTourTypes'

export type TransformPreference = {
  panePositions: Partial<Record<Pane, Position>>
  paneSizes: Partial<Record<Pane, Size>>
}

export const EMPTY_TRANSFORM: TransformPreference = { panePositions: {}, paneSizes: {} }

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}

function storedPosition(value: unknown): Position | undefined {
  if (!isRecord(value) || !Number.isFinite(value.left) || !Number.isFinite(value.top)) return undefined
  return { left: Number(value.left), top: Number(value.top) }
}

function storedSize(value: unknown): Size | undefined {
  if (!isRecord(value) || !Number.isFinite(value.width) || !Number.isFinite(value.height)) return undefined
  if (Number(value.width) <= 0 || Number(value.height) <= 0) return undefined
  return { width: Number(value.width), height: Number(value.height) }
}

export function sanitizeTransformPreference(value: TransformPreference): TransformPreference {
  if (!isRecord(value)) return EMPTY_TRANSFORM
  const rawPositions = isRecord(value.panePositions) ? value.panePositions : {}
  const rawSizes = isRecord(value.paneSizes) ? value.paneSizes : {}
  const panePositions: TransformPreference['panePositions'] = {}
  const paneSizes: TransformPreference['paneSizes'] = {}
  for (const pane of ['main', 'aside'] as const) {
    const position = storedPosition(rawPositions[pane])
    const size = storedSize(rawSizes[pane])
    if (position) panePositions[pane] = position
    if (size) paneSizes[pane] = size
  }
  return { panePositions, paneSizes }
}
