import { Target } from 'lucide-react'

import { ScenarioList } from '@/features/scenarios/components/ScenarioList'
import type { LearningUnit } from '@/features/units/types'

export function UnitScenarioHub({ unit }: { unit: LearningUnit }) {
  return (
    <section className="grid gap-4">
      <div className="flex items-start gap-3">
        <div className="grid size-10 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
          <Target className="size-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold">Scenario Skill Focuses</h3>
          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Choose a public Git skill focus, then open an available difficulty. A Skill Focus Preview appears before the
            real scenario workspace starts.
          </p>
        </div>
      </div>
      <ScenarioList scope="unit" unitId={unit.id} source="unit_card" />
    </section>
  )
}
