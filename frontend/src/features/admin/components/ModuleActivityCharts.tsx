import { AnalyticsInfo } from './AnalyticsInfo'
import { useState } from 'react'
import { Layers, Users } from 'lucide-react'
import type { PerformanceSummary } from '@/features/performance/types'
import { MODULES } from '../utils/kpiCatalogue'

export function ModuleActivityCharts({ activity }: { activity: PerformanceSummary['module_activity'] }) {
  const [measure, setMeasure] = useState<'attempted_tiers' | 'mastered_tiers'>('attempted_tiers')
  const rows = MODULES.map(module => ({ module, activity: activity?.find(row => row.number === module.num) }))
  const maxParticipants = Math.max(1, ...rows.map(row => row.activity?.participants ?? 0))
  const maxTiers = Math.max(1, ...rows.flatMap(row => (['attempted_tiers', 'mastered_tiers'] as const).map(key => row.activity?.difficulties.reduce((sum, item) => sum + item[key], 0) ?? 0)))

  return <div className="la-side">
    <section className="la-panel" aria-labelledby="la-participation-title">
      <h2 id="la-participation-title"><Users aria-hidden="true" />Learners per Module</h2>
      <p className="la-caption">How many learners have started each module.</p>
      <div className="la-horizontal-bars" role="group" aria-label="Unique learners by module">
        {rows.map(({ module, activity: row }) => <div className="la-horizontal-row" key={module.num} aria-label={`Module ${module.num}: ${row ? `${row.participants} unique learners` : 'unavailable'}`}>
          <span title={module.title}>Module {module.num}</span>
          <div className="la-track" aria-hidden="true"><span className="la-participant-fill" style={{ width: `${(row?.participants ?? 0) / maxParticipants * 100}%` }} /></div>
          <strong>{row?.participants ?? '—'}</strong>
        </div>)}
      </div>
      <AnalyticsInfo title="How learners are counted"><p>Each learner is counted once per module, including in-progress required tiers. Learners may appear in several modules, so these counts cannot be added to find the total learners.</p></AnalyticsInfo>
      {!activity && <p className="la-footnote" role="status">Per-module activity was not returned. Counts are unavailable.</p>}
    </section>
    <section className="la-panel" aria-labelledby="la-difficulty-title">
      <div className="la-heading"><h2 id="la-difficulty-title"><Layers aria-hidden="true" />Easy, Medium &amp; Hard Progress</h2>
        <label className="la-select"><span className="la-sr-only">Difficulty measure</span><select value={measure} onChange={event => setMeasure(event.target.value as typeof measure)}><option value="attempted_tiers">Attempted tiers</option><option value="mastered_tiers">Mastered tiers</option></select></label>
      </div>
      <p className="la-caption">{measure === 'attempted_tiers' ? 'Attempted tiers across learners, grouped by difficulty.' : 'Completed tiers across learners, grouped by difficulty.'}</p>
      <div className="la-count-heading"><span>Module</span><span>Total tiers</span></div><div className="la-horizontal-bars" role="group" aria-label={`${measure === 'attempted_tiers' ? 'Attempted' : 'Mastered'} learner tiers by difficulty`}>
        {rows.map(({ module, activity: row }) => <div className="la-horizontal-row" key={module.num}>
          <span title={module.title}>Module {module.num}</span><div className="la-track la-stacked">
            {row?.difficulties.map(item => <span key={item.difficulty} className={`la-difficulty-segment is-${item.difficulty}`} style={{ width: `${item[measure] / maxTiers * 100}%` }} title={`${item.difficulty}: ${item[measure]}`} aria-hidden="true" />)}
          </div><strong>{row ? row.difficulties.reduce((sum, item) => sum + item[measure], 0) : '—'}</strong>
          <span className="la-sr-only">Module {module.num}: {row ? row.difficulties.map(item => `${item.difficulty} ${item[measure]}`).join(', ') : 'unavailable'}</span>
        </div>)}
      </div>
      <div className="la-difficulty-legend"><span className="is-easy">Easy</span><span className="is-medium">Medium</span><span className="is-hard">Hard</span></div>
      <div className="la-count-axis" aria-hidden="true"><span>0</span><span>{maxTiers} tiers</span></div><p className="la-caption">One learner can contribute several tiers.</p>
      <AnalyticsInfo title="Counting rules and exact values">
        <p>A tier is one lesson difficulty. Each learner–tier pair counts once, so a learner can contribute several counts. Attempted includes a completed, failed or abandoned run, or a run with commands idle for at least 7 days. Open runs without an outcome remain in progress. Mastered requires recorded tier completion by the reporting cutoff, after clearing all required scenarios. Staff, replays, optional levels and transfer runs are excluded. This overview includes all-time activity. These counts are not percentages or a sequential learner funnel.</p>
        <table><caption>Exact {measure === 'attempted_tiers' ? 'attempted' : 'mastered'} learner–tier counts</caption><thead><tr><th>Module</th><th>Easy</th><th>Medium</th><th>Hard</th></tr></thead><tbody>{rows.map(({ module, activity: row }) => <tr key={module.num}><th>M{module.num}</th>{['easy', 'medium', 'hard'].map(difficulty => <td key={difficulty}>{row?.difficulties.find(item => item.difficulty === difficulty)?.[measure] ?? '—'}</td>)}</tr>)}</tbody></table>
      </AnalyticsInfo>
    </section>
  </div>
}
