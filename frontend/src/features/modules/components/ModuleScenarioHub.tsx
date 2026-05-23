import { Target } from 'lucide-react'

import { ScenarioList } from '@/features/scenarios/components/ScenarioList'
import type { ScenarioSkillFocus } from '@/features/scenarios/types'
import type { LearningModule } from '@/features/modules/types'

export function ModuleScenarioHub({
  module,
  scenarioSummary,
  scenarioSummaryPending = false,
}: {
  module: LearningModule
  scenarioSummary?: ScenarioSkillFocus[]
  scenarioSummaryPending?: boolean
}) {
  return (
    <section className="grid gap-4">
      <div className="flex items-start gap-3">
        <div className="grid size-10 place-items-center rounded-md border border-primary/30 bg-primary/10 text-primary">
          <Target className="size-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold">Scenarios</h3>
        </div>
      </div>
      <ScenarioList
        scope="module"
        moduleId={module.id}
        source="module_card"
        initialScenarios={scenarioSummary}
        deferFetch={scenarioSummaryPending}
      />
    </section>
  )
}
