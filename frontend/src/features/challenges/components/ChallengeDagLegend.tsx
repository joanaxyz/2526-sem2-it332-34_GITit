import { Circle, CircleDot, Diamond } from 'lucide-react'

/** Node legend at the foot of the DAG band, mirroring the reference mock. */
export function ChallengeDagLegend() {
  return (
    <div className="dag-legend" aria-hidden="true">
      <span>
        <CircleDot />
        HEAD
      </span>
      <span>
        <Circle />
        Branch
      </span>
      <span>
        <Diamond />
        Commit
      </span>
    </div>
  )
}
