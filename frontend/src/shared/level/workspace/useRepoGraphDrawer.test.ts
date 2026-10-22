import { act, renderHook } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { RepositorySnapshot } from '@/shared/level/types'

import { useRepoGraphDrawer } from './useRepoGraphDrawer'

// A controllable matchMedia: `setMatches` flips the drawer range on and off.
let matches = false
const listeners = new Set<() => void>()
function setMatches(next: boolean) {
  matches = next
  listeners.forEach((listener) => listener())
}

beforeEach(() => {
  matches = true
  vi.stubGlobal('matchMedia', (query: string) => ({
    get matches() {
      return matches
    },
    media: query,
    addEventListener: (_: string, listener: () => void) => listeners.add(listener),
    removeEventListener: (_: string, listener: () => void) => listeners.delete(listener),
  }))
})

afterEach(() => {
  vi.unstubAllGlobals()
  listeners.clear()
})

function snapshot(commits: string[]): RepositorySnapshot {
  return {
    repository_initialized: true,
    commits: commits.map((id, index) => ({ id, message: id, parents: index ? [commits[index - 1]] : [], tree: {} })),
    branches: { main: commits.at(-1) ?? null },
    head: { type: 'branch', name: 'main', target: commits.at(-1) ?? null },
    staging: {},
    working_tree: {},
    conflicts: [],
  } as unknown as RepositorySnapshot
}

function renderDrawer(initial: RepositorySnapshot) {
  return renderHook(({ state }: { state: RepositorySnapshot }) => useRepoGraphDrawer(state), {
    initialProps: { state: initial },
  })
}

describe('useRepoGraphDrawer', () => {
  it('starts closed with nothing flagged', () => {
    const { result } = renderDrawer(snapshot(['c1']))

    expect(result.current).toMatchObject({ drawerMode: true, open: false, hasUpdate: false, openCount: 0 })
  })

  it('flags a graph change made while the drawer is closed, and clears it once opened', () => {
    const { result, rerender } = renderDrawer(snapshot(['c1']))

    rerender({ state: snapshot(['c1', 'c2']) })
    expect(result.current.hasUpdate).toBe(true)

    act(() => result.current.openDrawer())
    expect(result.current).toMatchObject({ open: true, hasUpdate: false, openCount: 1 })

    act(() => result.current.closeDrawer())
    expect(result.current).toMatchObject({ open: false, hasUpdate: false })
  })

  it('ignores working-tree changes that the graph does not draw', () => {
    const { result, rerender } = renderDrawer(snapshot(['c1']))

    rerender({ state: { ...snapshot(['c1']), working_tree: { 'notes.md': 'draft' } } as RepositorySnapshot })

    expect(result.current.hasUpdate).toBe(false)
  })

  it('counts every opening so the diagrams refit', () => {
    const { result } = renderDrawer(snapshot(['c1']))

    act(() => result.current.openDrawer())
    act(() => result.current.closeDrawer())
    act(() => result.current.openDrawer())

    expect(result.current.openCount).toBe(2)
  })

  it('closes and stops flagging when the layout leaves the drawer range', () => {
    const { result, rerender } = renderDrawer(snapshot(['c1']))
    act(() => result.current.openDrawer())

    act(() => setMatches(false))
    rerender({ state: snapshot(['c1', 'c2']) })

    expect(result.current).toMatchObject({ drawerMode: false, open: false, hasUpdate: false })

    // Back in range, the drawer is closed and the change was already visible.
    act(() => setMatches(true))
    expect(result.current).toMatchObject({ drawerMode: true, open: false, hasUpdate: false })
  })
})
