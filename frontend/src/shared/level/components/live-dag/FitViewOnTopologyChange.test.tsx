import { act, cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { FitViewOnTopologyChange } from './FitViewOnTopologyChange'

const { fitView, getNodes, getEdges } = vi.hoisted(() => ({
  fitView: vi.fn(), getNodes: vi.fn(), getEdges: vi.fn(() => []),
}))
vi.mock('reactflow', () => ({
  useReactFlow: () => ({ fitView, getNodes, getEdges }),
  useStore: () => '400x300',
}))

afterEach(() => { cleanup(); vi.useRealTimers(); vi.clearAllMocks() })

describe('empty repository viewport fitting', () => {
  it.each([false, true])('centers the visible repository when initialized=%s', (initialized) => {
    vi.useFakeTimers()
    getNodes.mockReturnValue([{ id: '__empty__', data: { initialized } }])
    const signature = initialized ? 'empty' : 'folder'
    render(<FitViewOnTopologyChange fitSignature={signature} topologySignature={signature} fitViewPadding={0.16} />)
    act(() => { vi.advanceTimersByTime(200) })
    expect(fitView).toHaveBeenCalledOnce()
  })

  it('waits when React Flow still holds the previous initialization state', () => {
    vi.useFakeTimers()
    getNodes.mockReturnValue([{ id: '__empty__', data: { initialized: false } }])
    render(<FitViewOnTopologyChange fitSignature="empty" topologySignature="empty" fitViewPadding={0.16} />)
    act(() => { vi.advanceTimersByTime(200) })
    expect(fitView).not.toHaveBeenCalled()
  })
})
