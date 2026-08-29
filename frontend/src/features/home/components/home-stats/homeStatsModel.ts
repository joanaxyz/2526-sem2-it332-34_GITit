import type { HomeSummary } from '@/features/home/types'
import { deriveAchievements, type Achievement } from '@/features/home/utils/achievements'
import type { SkillAxis, StatsSummary, TrendPoint } from '@/features/stats/types'

export type HomeActivityCell = {
  key: string
  date: string
  value: number
}

export type HomeSkillProfileRow = SkillAxis & {
  command: string
}

type HomeRateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

export type HomeStatsDashboardModel = {
  skillRows: HomeSkillProfileRow[]
  activityCells: HomeActivityCell[]
  overallMastery: number
  masteryStars: number
  story: {
    levelsCompleted: number
    perfectClears: number
    hardTrialsWon: number
    trackProgress: number
  }
  kpis: {
    clearRate: HomeRateMetric
    hardClearRate: HomeRateMetric
    averageRetries: HomeRateMetric
    accuracy: number | null
    commandsRun: number
    accuracyReady: boolean
  }
}

export type HomeStatsModel = {
  dashboard: HomeStatsDashboardModel
  achievements: Achievement[]
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function average(values: number[]) {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function buildActivityCells(points: TrendPoint[]): HomeActivityCell[] {
  const recent = points.slice(-14)
  const padded = Array.from({ length: Math.max(0, 14 - recent.length) }, (_, index) => ({
    key: `empty-${index}`,
    date: '',
    value: 0,
  }))

  return [
    ...padded,
    ...recent.map((point) => ({
      key: point.date,
      date: point.date,
      value: point.commands_run + point.levels_completed * 4,
    })),
  ]
}

function buildSkillRows(axes: SkillAxis[]): HomeSkillProfileRow[] {
  return axes.map((axis) => ({
    ...axis,
    command: axis.command ?? axis.label,
  }))
}

export function buildHomeStatsModel(home: HomeSummary, stats: StatsSummary): HomeStatsModel {
  const skillValues = stats.skill_profile
    .map((axis) => axis.value)
    .filter((value): value is number => typeof value === 'number')
  const overallMastery = clampPercent(average(skillValues))

  return {
    dashboard: {
      skillRows: buildSkillRows(stats.skill_profile),
      activityCells: buildActivityCells(stats.activity_trend),
      overallMastery,
      masteryStars: Math.max(1, Math.min(3, Math.ceil(overallMastery / 34))),
      story: {
        levelsCompleted: stats.headline.levels_completed || home.counts.completed,
        perfectClears: Math.max(stats.headline.perfect_clears, home.perfect_clears),
        hardTrialsWon: stats.headline.boss_floors?.value ?? 0,
        trackProgress: clampPercent(stats.headline.finish_rate.value ?? 0),
      },
      kpis: {
        clearRate: { ...home.kpis.scr },
        hardClearRate: { ...home.kpis.hlcr },
        averageRetries: { ...home.kpis.arc },
        accuracy: stats.headline.accuracy,
        commandsRun: stats.headline.commands_run,
        accuracyReady: stats.headline.commands_run >= 100,
      },
    },
    achievements: deriveAchievements(home, stats),
  }
}
