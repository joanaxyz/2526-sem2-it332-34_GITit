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
  it('adapts the rich summaries into the complete dashboard and achievement ledger', () => {
    const model = buildHomeStatsModel(richHomeFixture, richStatsFixture)

    expect(model.dashboard.skillRows).toHaveLength(12)
    expect(model.dashboard.skillRows[0]).toMatchObject({ label: 'Initialize', command: 'git init', value: 100 })
    expect(model.dashboard.overallMastery).toBe(60)
    expect(model.dashboard.masteryStars).toBe(2)
    expect(model.dashboard.activityCells.map((cell) => cell.value)).toEqual([
      46, 26, 63, 52, 9, 83, 49, 70, 30, 88, 47, 104, 67, 55,
    ])
    expect(model.dashboard.story).toEqual({
      levelsCompleted: 43,
      perfectClears: 26,
      hardTrialsWon: 4,
      trackProgress: 76,
    })
    expect(model.dashboard.kpis).toEqual({
      clearRate: { value: 83, numerator: 39, denominator: 47 },
      hardClearRate: { value: 62, numerator: 8, denominator: 13 },
      averageRetries: { value: 1.6, numerator: 74, denominator: 47 },
      accuracy: 91,
      commandsRun: 1187,
      accuracyReady: true,
    })
    expect(model.achievements).toHaveLength(19)
    expect(model.achievements.filter((achievement) => achievement.unlocked)).toHaveLength(16)
  })

  it('pads an empty account to fourteen zero-value activity cells', () => {
    const model = buildHomeStatsModel(emptyHomeFixture, emptyStatsFixture)

    expect(model.dashboard.skillRows).toHaveLength(12)
    expect(model.dashboard.overallMastery).toBe(0)
    expect(model.dashboard.masteryStars).toBe(1)
    expect(model.dashboard.activityCells).toHaveLength(14)
    expect(model.dashboard.activityCells.every((cell) => cell.date === '' && cell.value === 0)).toBe(true)
    expect(model.dashboard.story).toEqual({
      levelsCompleted: 0,
      perfectClears: 0,
      hardTrialsWon: 0,
      trackProgress: 0,
    })
    expect(model.dashboard.kpis.accuracyReady).toBe(false)
  })

  it('keeps only the latest fourteen activity points and weights completed levels by four', () => {
    const stats = structuredClone(richStatsFixture)
    stats.activity_trend = Array.from({ length: 16 }, (_, index) => ({
      date: `2026-07-${String(index + 1).padStart(2, '0')}`,
      commands_run: index,
      levels_completed: 1,
    }))

    const model = buildHomeStatsModel(richHomeFixture, stats)

    expect(model.dashboard.activityCells).toHaveLength(14)
    expect(model.dashboard.activityCells[0]).toEqual({ key: '2026-07-03', date: '2026-07-03', value: 6 })
    expect(model.dashboard.activityCells.at(-1)).toEqual({ key: '2026-07-16', date: '2026-07-16', value: 19 })
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

    expect(model.dashboard.skillRows.at(-1)?.command).toBe('Fallback command')
    expect(model.dashboard.overallMastery).toBe(65)
    expect(model.dashboard.masteryStars).toBe(2)
    expect(model.dashboard.story).toMatchObject({ levelsCompleted: 43, perfectClears: 30, trackProgress: 100 })
    expect(model.dashboard.kpis).toMatchObject({ accuracy: 95, commandsRun: 99, accuracyReady: false })
  })

  it('does not mutate frozen source summaries or share KPI metric objects', () => {
    const home = deepFreeze(structuredClone(richHomeFixture))
    const stats = deepFreeze(structuredClone(richStatsFixture))

    const model = buildHomeStatsModel(home, stats)

    expect(model.dashboard.kpis.clearRate).not.toBe(home.kpis.scr)
    expect(model.dashboard.kpis.hardClearRate).not.toBe(home.kpis.hlcr)
    expect(model.dashboard.kpis.averageRetries).not.toBe(home.kpis.arc)
  })
})
