import { UnitScenarioList } from '@/features/units/components/UnitScenarioList'

export function ViewScenariosPanel({ unitId }: { unitId: number }) {
  return (
    <section className="mt-6 rounded-lg border border-border bg-card p-5">
      <div className="mb-4">
        <h2 className="text-xl font-bold">View Scenarios</h2>
        <p className="mt-1 text-sm text-muted-foreground">Select a scenario skill focus, then choose an available difficulty.</p>
      </div>
      <UnitScenarioList unitId={unitId} source="lesson_overview" />
    </section>
  )
}
