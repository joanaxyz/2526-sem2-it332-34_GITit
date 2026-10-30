import { useCallback, useEffect, useReducer } from 'react'

import type { ApiSchemas } from '@/shared/api/generated/apiTypes'

export type LearnedSkill = ApiSchemas['LearnedSkillResponse']

type QueueState = {
  runId: number | null
  skills: LearnedSkill[]
  seen: Set<string>
}
type QueueAction =
  | { type: 'reset'; runId: number | null }
  | { type: 'enqueue'; runId: number | null; skills: LearnedSkill[] }
  | { type: 'dismiss'; runId: number | null }

function reducer(state: QueueState, action: QueueAction): QueueState {
  if (action.type === 'reset') {
    return state.runId === action.runId ? state : { runId: action.runId, skills: [], seen: new Set() }
  }
  // A late response from a run the player has left must not replace its successor's queue.
  if (action.runId !== state.runId) return state
  if (action.type === 'dismiss') return { ...state, skills: state.skills.slice(1) }

  const seen = new Set(state.seen)
  const skills = action.skills.filter((skill) => {
    const family = skill.base_command.trim().toLowerCase()
    if (seen.has(family)) return false
    seen.add(family)
    return true
  })
  return skills.length ? { ...state, seen, skills: [...state.skills, ...skills] } : state
}

/** Only enqueue the server's newly learned command events, never query or level metadata. */
export function useSkillLearnedQueue({ runId, blocked }: { runId: number | null; blocked: boolean }) {
  const [state, dispatch] = useReducer(reducer, { runId, skills: [], seen: new Set<string>() })
  useEffect(() => dispatch({ type: 'reset', runId }), [runId])

  const enqueue = useCallback((skills: LearnedSkill[]) => {
    if (skills.length) dispatch({ type: 'enqueue', runId, skills })
  }, [runId])
  const dismiss = useCallback(() => dispatch({ type: 'dismiss', runId }), [runId])
  const pending = state.runId === runId && state.skills.length > 0

  return { enqueue, dismiss, pending, skill: pending && !blocked ? state.skills[0] : null }
}
