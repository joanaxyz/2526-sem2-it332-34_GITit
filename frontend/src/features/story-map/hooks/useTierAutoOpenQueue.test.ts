import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import { hasSeenTierStory, markTierStorySeen } from '@/features/story-map/utils/tierStorySeen'
import { hasSeenLevelTour, markLevelTourSeen } from '@/shared/level/utils/levelTour'

import { useTierAutoOpenQueue } from './useTierAutoOpenQueue'

const level = { userId: 7, adventureLevelId: 12, difficulty: 'easy' as const }

function renderQueue(started = true) {
  return renderHook((props: { started: boolean }) => useTierAutoOpenQueue({ ...level, started: props.started }), {
    initialProps: { started },
  })
}

describe('useTierAutoOpenQueue', () => {
  afterEach(() => window.localStorage.clear())

  it('opens the story, then the tour, then allows the command guide, one at a time', () => {
    const { result } = renderQueue()

    expect(result.current).toMatchObject({ storyOpen: true, tourOpen: false, guideAllowed: false })

    act(() => result.current.closeStory())
    expect(result.current).toMatchObject({ storyOpen: false, tourOpen: true, guideAllowed: false })
    expect(hasSeenTierStory(7, 12, 'easy')).toBe(true)

    act(() => result.current.closeTour())
    expect(result.current).toMatchObject({ storyOpen: false, tourOpen: false, guideAllowed: true })
    expect(hasSeenLevelTour(7, 'tier')).toBe(true)
  })

  it('skips straight to the guide when the story and tour were already seen', () => {
    markTierStorySeen(7, 12, 'easy')
    markLevelTourSeen(7, 'tier')

    const { result } = renderQueue()

    expect(result.current).toMatchObject({ storyOpen: false, tourOpen: false, guideAllowed: true })
  })

  it('reopens the story on request without letting the tour or guide stack on it', () => {
    markTierStorySeen(7, 12, 'easy')
    const { result } = renderQueue()
    expect(result.current.tourOpen).toBe(true)

    act(() => result.current.openStory())
    expect(result.current).toMatchObject({ storyOpen: true, tourOpen: false, guideAllowed: false })

    act(() => result.current.closeStory())
    expect(result.current).toMatchObject({ storyOpen: false, tourOpen: true })
  })

  it('auto-opens nothing for a run that is not in progress', () => {
    const { result } = renderQueue(false)

    expect(result.current).toMatchObject({ storyOpen: false, tourOpen: false, guideAllowed: true })
  })

  it('waits for the run before deciding about the story', () => {
    const { result } = renderHook(() =>
      useTierAutoOpenQueue({ userId: 7, adventureLevelId: undefined, difficulty: undefined, started: false }),
    )

    expect(result.current.storyOpen).toBe(false)
  })
})
