import { GitFork, Laptop, Server } from 'lucide-react'

export function CentralizedDistributedDiagram({ active }: { active: 'centralized' | 'distributed' | null }) {
  return (
    <div className="orientation-model-diagram">
      <section className={active === 'centralized' ? 'is-active' : undefined} aria-label="Centralized version control model">
        <header><Server aria-hidden="true" /><strong>Centralized</strong></header>
        <div className="orientation-centralized-map" aria-hidden="true">
          <span className="orientation-server-node">One history</span>
          <div><span><Laptop /> Client A</span><span><Laptop /> Client B</span></div>
        </div>
        <p>One server holds the authoritative history. If it is unavailable, most collaboration stops.</p>
      </section>
      <section className={active === 'distributed' ? 'is-active' : undefined} aria-label="Distributed version control model">
        <header><GitFork aria-hidden="true" /><strong>Distributed</strong></header>
        <div className="orientation-distributed-map" aria-hidden="true">
          {['Clone A', 'Clone B', 'Clone C'].map((label) => <span key={label}><Laptop /> {label}<small>full history</small></span>)}
        </div>
        <p>Every clone carries complete history. A remote coordinates sharing, but local work remains possible.</p>
      </section>
    </div>
  )
}
