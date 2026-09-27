import { useEffect, useState } from 'react'

import type { CommandIntroduction } from '@/features/story-map/api/commandIntroductionsApi'

const HISTORY_KEY_PREFIX = 'git-it-command-guides:'

function storage() {
  if (typeof window === 'undefined') return null
  try {
    return window.sessionStorage
  } catch {
    return null
  }
}

function isCommandGuide(value: unknown): value is CommandIntroduction {
  if (!value || typeof value !== 'object') return false
  const guide = value as Partial<CommandIntroduction>
  return typeof guide.teaching_key === 'string'
    && typeof guide.title === 'string'
    && Boolean(guide.command_form && typeof guide.command_form.usage_form === 'string')
}

export function loadCommandGuideHistory(runId: number) {
  const store = storage()
  if (!store || !Number.isFinite(runId)) return []
  try {
    const value: unknown = JSON.parse(store.getItem(`${HISTORY_KEY_PREFIX}${runId}`) ?? '[]')
    return Array.isArray(value) ? value.filter(isCommandGuide) : []
  } catch {
    return []
  }
}

export function rememberCommandGuide(
  guides: CommandIntroduction[],
  tutor: CommandIntroduction,
) {
  if (guides.some((guide) => guide.teaching_key === tutor.teaching_key)) return guides
  return [...guides, { ...tutor, completion_token: null }]
}

function saveCommandGuideHistory(runId: number, guides: readonly CommandIntroduction[]) {
  const store = storage()
  if (!store || !Number.isFinite(runId)) return
  try {
    store.setItem(`${HISTORY_KEY_PREFIX}${runId}`, JSON.stringify(guides))
  } catch {
    // Session storage can be blocked; in-memory guide history still works.
  }
}

export function useCommandGuideHistory(
  runId: number,
  tutor?: CommandIntroduction | null,
) {
  const [guides, setGuides] = useState<CommandIntroduction[]>(() => loadCommandGuideHistory(runId))

  useEffect(() => {
    setGuides(loadCommandGuideHistory(runId))
  }, [runId])

  useEffect(() => {
    if (!tutor) return
    setGuides((current) => {
      const next = rememberCommandGuide(current, tutor)
      if (next !== current) saveCommandGuideHistory(runId, next)
      return next
    })
  }, [runId, tutor])

  return guides
}
