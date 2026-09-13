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

    // The fixture mirrors the published catalog: eighteen commands, real titles.
    expect(model.skills.rows).toHaveLength(18)
    expect(model.skills.rows[0]).toMatchObject({ label: 'git init', command: 'git init', short: 'init', value: 100 })
    expect(model.skills.overallMastery).toBe(54)
    expect(model.skills.masteryStars).toBe(2)
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
    // Hard trials won and the clear rate are gone: the record band's hard-run
    // tile and the citadel already state them, and one screen states a fact once.
    expect(model.results).toEqual({
      hardClearRate: { value: 62, numerator: 8, denominator: 13 },
      averageRetries: { value: 1.6, numerator: 74, denominator: 47 },
      accuracy: 91,
      commandsRun: 1187,
      accuracyReady: true,
    })
    expect(model.achievements).toHaveLength(19)
    expect(model.achievements.filter((achievement) => achievement.unlocked)).toHaveLength(16)
  })

  it('plots nothing at all for an account with no trend', () => {
    const model = buildHomeStatsModel(emptyHomeFixture, emptyStatsFixture)

    expect(model.skills.rows).toHaveLength(18)
    expect(model.skills.overallMastery).toBe(0)
    expect(model.skills.masteryStars).toBe(1)
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
    expect(model.results.accuracyReady).toBe(false)
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

  it('preserves fallbacks, clamps percentages, and applies the accuracy threshold', () => {
    const home = structuredClone(richHomeFixture)
    const stats = structuredClone(richStatsFixture)
    stats.skill_profile = [
      { key: 'low', label: 'Low', hint: 'Low value', value: -20, command: 'Low' },
      { key: 'high', label: 'High', hint: 'High value', value: 150, command: 'High' },
      {
        key: 'missing',
        label: 'Fallback command',
        hint: 'No value',
        value: null,
        command: 'Fallback command',
      },
    ]
    stats.headline.levels_completed = 0
    stats.headline.perfect_clears = 30
    stats.headline.finish_rate.value = 120
    stats.headline.commands_run = 99
    stats.headline.accuracy = 95

    const model = buildHomeStatsModel(home, stats)

    expect(model.skills.rows.at(-1)?.command).toBe('Fallback command')
    // The radar rim wears the machine name, so "git add" becomes "add".
    expect(model.skills.rows.map((row) => row.short)).toEqual(['Low', 'High', 'Fallback command'])
    expect(buildHomeStatsModel(home, richStatsFixture).skills.rows[4].short).toBe('add')
    expect(model.skills.overallMastery).toBe(65)
    expect(model.skills.masteryStars).toBe(2)
    expect(model.progress.story).toMatchObject({
      levelsCompleted: 43,
      perfectClears: 30,
      finishRate: { value: 100 },
    })
    expect(model.results).toMatchObject({ accuracy: 95, commandsRun: 99, accuracyReady: false })
  })

  it('does not mutate frozen source summaries or share KPI metric objects', () => {
    const home = deepFreeze(structuredClone(richHomeFixture))
    const stats = deepFreeze(structuredClone(richStatsFixture))

    const model = buildHomeStatsModel(home, stats)

    expect(model.progress.story.finishRate).not.toBe(stats.headline.finish_rate)
    expect(model.results.hardClearRate).not.toBe(home.kpis.hlcr)
    expect(model.results.averageRetries).not.toBe(home.kpis.arc)
  })
})
