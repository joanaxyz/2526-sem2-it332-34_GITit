import { Check, FileCode2 } from 'lucide-react'

const STAGES = [
  { id: 'working_tree', label: 'Working tree', detail: 'Edited on disk' },
  { id: 'staging', label: 'Staging area', detail: 'Selected for commit' },
  { id: 'local_repo', label: 'Local repository', detail: 'Saved in history' },
  { id: 'remote', label: 'Remote', detail: 'Shared with the team' },
]

export function FourAreaPipelineDiagram({
  activeIndex,
  onSelectStage,
}: {
  activeIndex: number
  onSelectStage: (index: number) => void
}) {
  return (
    <div className="orientation-pipeline" aria-label="The four areas of Git">
      <div className="orientation-pipeline-track" aria-hidden="true">
        <span style={{ width: `${(activeIndex / (STAGES.length - 1)) * 100}%` }} />
      </div>
      {STAGES.map((stage, index) => {
        const reached = index <= activeIndex
        return (
          <button
            key={stage.id}
            type="button"
            className={reached ? 'is-reached' : undefined}
            aria-current={index === activeIndex ? 'step' : undefined}
            aria-label={`${stage.label}: ${stage.detail}${index === activeIndex ? ', current area' : ''}`}
            onClick={() => onSelectStage(index)}
          >
            <span className="orientation-pipeline-node" aria-hidden="true">
              {index < activeIndex ? <Check /> : <FileCode2 />}
            </span>
            <strong>{stage.label}</strong>
            <small>{stage.detail}</small>
          </button>
        )
      })}
    </div>
  )
}
