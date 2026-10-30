import type { ApiSchemas } from '@/shared/api/generated/apiTypes'
export function CommandComparison({ comparison }: { comparison?: ApiSchemas['CommandComparisonResponse'] | null }) {
 if (!comparison) return null
 const { learner_count: used, example_count: example } = comparison
 return <section className="star-checklist outcome-comparison" aria-label="Solution command comparison"><p>Scenario completed in {used} counted {used === 1 ? 'command' : 'commands'}! <strong>Our example solution uses {example} {example === 1 ? 'command' : 'commands'}.</strong></p>{used < example ? <p>{example-used} fewer {example-used === 1 ? 'command' : 'commands'} than the example.</p> : null}</section>
}
