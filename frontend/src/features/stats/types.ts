type RateMetric = {
  value: number | null
  numerator: number
  denominator: number
}

export type GitSkillMastery = {
  key: string
  command: string
  label: string
  hint: string
  value: number | null
}

export type TrendPoint = {
  date: string
  levels_completed: number
  commands_run: number
}

type ScopedCount = {
  value: number
  scope: string
}

export type StatsSummary = {
  skill_profile: GitSkillMastery[]
  activity_trend: TrendPoint[]
  headline: {
    levels_completed: number
    finish_rate: RateMetric
    accuracy: number | null
    boss_floors: ScopedCount
    comebacks: ScopedCount
    perfect_clears: number
    day_streak: number
    longest_streak: number
    gitcoins: number
    commands_run: number
  }
}
