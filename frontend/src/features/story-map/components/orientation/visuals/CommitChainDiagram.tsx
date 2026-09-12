import { ArrowRight, GitCommitHorizontal } from 'lucide-react'

export function CommitChainDiagram({ amended }: { amended?: boolean }) {
  return (
    <div className="orientation-commit-chain">
      <div aria-label={amended ? 'Original commit now points to a new amended commit' : 'Original commit with a pending amended copy'}>
        <span><GitCommitHorizontal aria-hidden="true" /><code>a1b2c3d</code><small>original</small></span>
        <ArrowRight aria-hidden="true" />
        <span className={amended ? 'is-amended' : 'is-pending'}>
          <GitCommitHorizontal aria-hidden="true" />
          <code>{amended ? 'f9e8d7c' : '•••••••'}</code>
          <small>{amended ? 'new commit' : 'amended copy'}</small>
        </span>
      </div>
      <p>Amend writes a new object and moves the branch pointer. It never mutates the old hash.</p>
    </div>
  )
}

const FIELD_EXPLANATIONS: Record<string, string> = {
  hash: 'Uniquely identifies the commit. Any content or metadata change produces a different hash.',
  author: 'Records who originally wrote the change for review history and blame.',
  timestamp: 'Places the commit on a timeline for inspection and auditing.',
  message: 'Explains intent and context, not just which files changed.',
  tree: 'Stores the complete tracked-file snapshot at this point in history.',
  parent: 'Links this commit to earlier history and creates the graph structure.',
}

const FIELDS = [
  { id: 'hash', label: 'Hash (SHA-1)', sample: 'a1b2c3d' },
  { id: 'author', label: 'Author', sample: 'Alex <alex@example.com>' },
  { id: 'timestamp', label: 'Timestamp', sample: '2026-05-28 10:00' },
  { id: 'message', label: 'Message', sample: 'Add login validation' },
  { id: 'tree', label: 'Tree snapshot', sample: 'files at commit time' },
  { id: 'parent', label: 'Parent pointer', sample: '→ previous commit' },
]

export function CommitAnatomyDiagram({ highlight }: { highlight: string | null }) {
  const active = FIELDS.find((field) => field.id === highlight)
  return (
    <div className="orientation-commit-anatomy">
      <div className="orientation-commit-object" aria-label="Commit object fields">
        <header><GitCommitHorizontal aria-hidden="true" /> commit object</header>
        <dl>
          {FIELDS.map((field) => (
            <div key={field.id} className={highlight === field.id ? 'is-active' : undefined}>
              <dt>{field.label}</dt><dd>{field.sample}</dd>
            </div>
          ))}
        </dl>
      </div>
      <aside aria-live="polite">
        <strong>{active?.label ?? 'Select a field'}</strong>
        <p>{active ? FIELD_EXPLANATIONS[active.id] : 'Inspect each field to understand what a commit records and how Git connects history.'}</p>
      </aside>
    </div>
  )
}
