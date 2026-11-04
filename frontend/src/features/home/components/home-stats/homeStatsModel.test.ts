import { describe, expect, it } from 'vitest'

import { emptyHomeFixture, richHomeFixture } from '@/features/home/preview/fixtures'
import { emptyStatsFixture, richStatsFixture } from '@/features/stats/preview/fixtures'

import { buildHomeStatsModel } from './homeStatsModel'

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value)
    Object.values(value).forEach(deepFreeze)
  }
  return value
}

describe('buildHomeStatsModel', () => {
  it('adapts the rich summaries into every Overview view slice and the achievement ledger', () => {
    const model = buildHomeStatsModel(richHomeFixture, richStatsFixture)

    // A month of daily points, exactly as the backend served them.
    expect(model.progress.activity.points).toHaveLength(30)
    expect(model.progress.activity.points[0]).toEqual({
      date: '2026-05-15',
      label: 'May 15',
      caption: 'Fri, May 15',
      commandsRun: 0,
      levelsCompleted: 0,
    })
    // Totals, active buckets and the peak all come off the same window, so the
    // caption under the plot can never disagree with the plot.
    expect(model.progress.activity).toMatchObject({
      commandsRun: 1084,
      levelsCompleted: 56,
      activeBuckets: 27,
      peakIndex: 25,
      peakLabel: '84 on Jun 9',
      resolvedWindow: 'month',
      heading: 'Last 30 days',
      bucket: 'days',
    })
    expect(model.progress.story).toEqual({
      levelsCompleted: 43,
      perfectClears: 26,
      finishRate: { value: 76, numerator: 43, denominator: 57 },
    })
    expect(model.achievements).toHaveLength(19)
    expect(model.achievements.filter((achievement) => achievement.unlocked)).toHaveLength(13)
  })

  it('plots nothing at all for an account with no trend', () => {
    const model = buildHomeStatsModel(emptyHomeFixture, emptyStatsFixture)

    // An empty window is drawn as an empty state, never as fourteen fake days.
    expect(model.progress.activity.points).toEqual([])
    expect(model.progress.activity).toMatchObject({
      commandsRun: 0,
      levelsCompleted: 0,
      activeBuckets: 0,
      peakIndex: -1,
      peakLabel: null,
    })
    expect(model.progress.story).toEqual({
      levelsCompleted: 0,
      perfectClears: 0,
      finishRate: { value: null, numerator: 0, denominator: 0 },
    })
  })

  it('plots exactly the window it was served, and labels monthly buckets by month', () => {
    const stats = structuredClone(richStatsFixture)
    // The span is a request parameter now, so the client plots what arrived
    // rather than trimming or padding it to a fixed cell count.
    stats.activity_trend = Array.from({ length: 16 }, (_, index) => ({
      date: `2026-07-${String(index + 1).padStart(2, '0')}`,
      commands_run: index,
      levels_completed: 1,
    }))

    const daily = buildHomeStatsModel(richHomeFixture, stats)

    expect(daily.progress.activity.points).toHaveLength(16)
    expect(daily.progress.activity.points[0]).toMatchObject({ date: '2026-07-01', commandsRun: 0 })
    expect(daily.progress.activity.peakIndex).toBe(15)

    stats.activity_window = 'year'
    stats.activity_trend = [
      { date: '2026-05-01', commands_run: 120, levels_completed: 4 },
      { date: '2026-06-01', commands_run: 310, levels_completed: 9 },
    ]

    const yearly = buildHomeStatsModel(richHomeFixture, stats)

    expect(yearly.progress.activity.points.map((point) => point.label)).toEqual(['May', 'Jun'])
    expect(yearly.progress.activity.points[1].caption).toBe('June 2026')
    expect(yearly.progress.activity).toMatchObject({
      peakLabel: '310 in Jun',
      heading: 'Last 12 months',
      bucket: 'months',
    })
  })

  it('clamps percentages and keeps tier counts exact', () => {
    const home = structuredClone(richHomeFixture)
    const stats = structuredClone(richStatsFixture)
    stats.headline.levels_completed = 0
    stats.headline.perfect_clears = 30
    stats.headline.finish_rate.value = 120
    stats.headline.commands_run = 99
    stats.headline.accuracy = 95

    const model = buildHomeStatsModel(home, stats)

    expect(model.progress.story).toMatchObject({
      levelsCompleted: 0,
      perfectClears: 30,
      finishRate: { value: 100 },
    })
  })

  it('does not mutate frozen source summaries or share KPI metric objects', () => {
    const home = deepFreeze(structuredClone(richHomeFixture))
    const stats = deepFreeze(structuredClone(richStatsFixture))

    const model = buildHomeStatsModel(home, stats)

    expect(model.progress.story.finishRate).not.toBe(stats.headline.finish_rate)
  })
})
