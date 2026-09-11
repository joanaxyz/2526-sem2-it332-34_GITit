/** Node legend at the foot of the DAG band, mirroring the reference mock. */
export function ChallengeDagLegend() {
  return (
    <div className="dag-legend" aria-hidden="true">
      <span>
        <i className="dag-legend-symbol is-head" />
        HEAD
      </span>
      <span>
        <i className="dag-legend-symbol is-branch" />
        Branch
      </span>
      <span>
        <i className="dag-legend-symbol is-commit" />
        Commit
      </span>
    </div>
  )
}
