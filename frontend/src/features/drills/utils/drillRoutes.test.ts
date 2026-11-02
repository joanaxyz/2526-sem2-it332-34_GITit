import { describe, expect, it } from 'vitest'
import { DRILL_PLAN_FIXTURE } from '@/features/dev/utils/drillPlan'
import { drillPracticePath } from './drillRoutes'

describe('drill practice destinations', () => {
  it('opens the owning chapter and exact level on the story map', () => {
    const plan = { ...DRILL_PLAN_FIXTURE, level: { ...DRILL_PLAN_FIXTURE.level, id: 51, chapter_id: 3, story_slug: 'arcane-spire' } }
    expect(drillPracticePath(plan)).toBe('/stories/arcane-spire?chapter=3&level=51')
  })

  it('uses the default story when the payload has no story and omits an absent chapter', () => {
    const plan = { ...DRILL_PLAN_FIXTURE, level: { ...DRILL_PLAN_FIXTURE.level, id: 51, chapter_id: null, story_slug: '' } }
    expect(drillPracticePath(plan)).toBe('/stories/arcane-spire?level=51')
  })
})
