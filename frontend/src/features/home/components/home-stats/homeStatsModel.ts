import type { HomeSummary } from '@/features/home/types'
import { deriveAchievements, type Achievement } from '@/features/home/utils/achievements'
import type { SkillAxis, StatsSummary, TrendPoint } from '@/features/stats/types'
import { activityWindowOption, type ActivityWindow } from '@/features/stats/utils/activityWindow'

export type HomeActivityPoint = {
  date: string
  /** Axis tick: "Jun 9" for a day bucket, "Jun" for a month of them. */
  label: string
  /** Tooltip title, spelled out: "Mon, Jun 9" or "June 2026". */
  caption: string
  commandsRun: number
  levelsCompleted: number
}

export type HomeSkillProfileRow = SkillAxis & {
  command: string
  /** Machine name for the radar rim, e.g. "add". */
  short: string
}

type HomeRateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

/** Progress, upper band: where this account stands in the story right now. */
export type HomeProgressModel = {
  activity: {
    points: HomeActivityPoint[]
    commandsRun: number
    levelsCompleted: number
    /** Buckets with any activity in them, out of `points.length`. */
    activeBuckets: number
    /** Index of the busiest bucket, or -1 when the span holds nothing. */
    peakIndex: number
    /** Direct label for that bucket, phrased for the bucket's unit. */
    peakLabel: string | null
    /**
     * The span these points actually cover, as the backend resolved it — not
     * the one the control has selected. While a new span is in flight the two
     * differ, and the plot must describe the data it is drawing.
     */
    resolvedWindow: ActivityWindow
    heading: string
    bucket: 'days' | 'months'
  }
  story: {
    levelsCompleted: number
    perfectClears: number
    /**
     * The share of started runs that were finished. The backend derives
     * `headline.finish_rate` and `kpis.scr` from the same two counts, so this is
     * the screen's only finish-rate fact and the record band never restates it.
     */
    finishRate: HomeRateMetric
  }
}

/** Overview view "Git skills": how reliably each command family is used. */
export type HomeSkillsModel = {
  rows: HomeSkillProfileRow[]
  overallMastery: number
  masteryStars: number
}

/** Progress, lower band: this account's record across everything played. */
export type HomeResultsModel = {
  hardClearRate: HomeRateMetric
  averageRetries: HomeRateMetric
  accuracy: number | null
  commandsRun: number
  accuracyReady: boolean
}

export type HomeStatsModel = {
  progress: HomeProgressModel
  skills: HomeSkillsModel
  results: HomeResultsModel
  achievements: Achievement[]
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function average(values: number[]) {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function bucketLabels(iso: string, monthly: boolean) {
  const day = new Date(`${iso}T00:00:00`)
  return monthly
    ? {
        label: day.toLocaleDateString('en-US', { month: 'short' }),
        caption: day.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
      }
    : {
        label: day.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        caption: day.toLocaleDateString('en-US', { weekday: 'short', month: 'long', day: 'numeric' }),
      }
}

/**
 * The span the backend returned, plotted as it arrived. The client no longer
 * trims or pads the series: the span is a request parameter now, so re-shaping
 * the answer here could only ever disagree with what was asked for.
 */
function buildActivity(stats: StatsSummary): HomeProgressModel['activity'] {
  const option = activityWindowOption(stats.activity_window)
  const monthly = option.bucket === 'months'
  const points = stats.activity_trend.map((point: TrendPoint) => ({
    date: point.date,
    ...bucketLabels(point.date, monthly),
    commandsRun: point.commands_run,
    levelsCompleted: point.levels_completed,
  }))

  let peakIndex = -1
  points.forEach((point, index) => {
    if (point.commandsRun > 0 && (peakIndex < 0 || point.commandsRun > points[peakIndex].commandsRun)) {
      peakIndex = index
    }
  })

  const peak = peakIndex >= 0 ? points[peakIndex] : null

  return {
    points,
    peakLabel: peak
      ? `${peak.commandsRun.toLocaleString()} ${monthly ? 'in' : 'on'} ${peak.label}`
      : null,
    commandsRun: points.reduce((sum, point) => sum + point.commandsRun, 0),
    levelsCompleted: points.reduce((sum, point) => sum + point.levelsCompleted, 0),
    activeBuckets: points.filter((point) => point.commandsRun > 0 || point.levelsCompleted > 0).length,
    peakIndex,
    resolvedWindow: stats.activity_window,
    heading: option.heading,
    bucket: option.bucket,
  }
}

function buildSkillRows(axes: SkillAxis[]): HomeSkillProfileRow[] {
  return axes.map((axis) => {
    const command = axis.command ?? axis.label
    return { ...axis, command, short: command.replace(/^git\s+/, '') }
  })
}

export function buildHomeStatsModel(home: HomeSummary, stats: StatsSummary): HomeStatsModel {
  const skillValues = stats.skill_profile
    .map((axis) => axis.value)
    .filter((value): value is number => typeof value === 'number')
  const overallMastery = clampPercent(average(skillValues))

  return {
    progress: {
      activity: buildActivity(stats),
      story: {
        levelsCompleted: stats.headline.levels_completed || home.counts.completed,
        perfectClears: Math.max(stats.headline.perfect_clears, home.perfect_clears),
        finishRate: {
          ...stats.headline.finish_rate,
          value:
            stats.headline.finish_rate.value === null
              ? null
              : clampPercent(stats.headline.finish_rate.value),
        },
      },
    },
    skills: {
      rows: buildSkillRows(stats.skill_profile),
      overallMastery,
      masteryStars: Math.max(1, Math.min(3, Math.ceil(overallMastery / 34))),
    },
    results: {
      // `home.kpis.scr` is deliberately unused: it is the same finish rate the
      // citadel already shows, and one fact per screen means one statement.
      hardClearRate: { ...home.kpis.hlcr },
      averageRetries: { ...home.kpis.arc },
      accuracy: stats.headline.accuracy,
      commandsRun: stats.headline.commands_run,
      accuracyReady: stats.headline.commands_run >= 100,
    },
    achievements: deriveAchievements(home, stats),
  }
}
