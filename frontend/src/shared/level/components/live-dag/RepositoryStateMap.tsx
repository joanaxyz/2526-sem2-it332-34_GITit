import type { RepositorySnapshot, RepositoryValue } from '@/shared/level/types'

function describe(value: RepositoryValue): string {
  if (value === null) return 'deleted'
  if (typeof value === 'object' && !Array.isArray(value) && typeof value.status === 'string') return value.status
  return 'changed'
}

function FileArea({ label, entries, empty }: {
  label: string; entries: Record<string, RepositoryValue>; empty: string
}) {
  const files = Object.entries(entries).sort(([left], [right]) => left.localeCompare(right))
  return (
    <details className="repository-state-map__area" open={files.length > 0}>
      <summary>{label} <span>{files.length}</span></summary>
      {files.length ? <ul>{files.map(([path, value]) => (
        <li key={path}><code>{path}</code><small>{describe(value)}</small></li>
      ))}</ul> : <p>{empty}</p>}
    </details>
  )
}

export function RepositoryStateMap({ snapshot }: { snapshot: RepositorySnapshot }) {
  const initialized = snapshot.repository_initialized !== false
  const remotes = Object.entries(snapshot.remotes ?? {})
  const config = Object.entries(snapshot.config ?? {})
  const stash = snapshot.stash_stack ?? []
  const refs = [
    ...Object.entries(snapshot.branches ?? {}).map(([name, target]) => `${name} → ${target ?? 'no commit yet'}`),
    ...Object.entries(snapshot.remote_branches ?? {}).map(([name, target]) => `${name} → ${target ?? 'no commit yet'}`),
    ...Object.keys(snapshot.tags ?? {}).map((name) => `tag: ${name}`),
  ]
  return (
    <section className="repository-state-map app-scrollbar" aria-label="Repository state">
      <p className="repository-state-map__metadata" data-initialized={initialized} role="status">
        <strong>{initialized ? 'Git repository' : 'Ordinary folder'}</strong>
        <span>{initialized ? '.git metadata present' : '.git metadata absent'}</span>
      </p>
      <div className="repository-state-map__flow">
        <FileArea label={initialized ? 'Working changes' : 'Files'} entries={snapshot.working_tree}
          empty={initialized ? 'No unstaged changes' : 'No files yet'} />
        <span className="repository-state-map__arrow" aria-hidden="true">→</span>
        <FileArea label="Staging area" entries={snapshot.staging}
          empty={initialized ? 'Nothing staged' : 'Not created yet'} />
      </div>
      <div className="repository-state-map__extras">
        {snapshot.conflicts.length ? <p role="status">Conflicts: {snapshot.conflicts.join(', ')}</p> : null}
        {initialized && refs.length ? <details><summary>References · {refs.length}</summary>
          <ul>{refs.map((ref) => <li key={ref}><code>{ref}</code></li>)}</ul>
        </details> : null}
        {remotes.length ? <details><summary>Remotes · {remotes.length}</summary>
          <ul>{remotes.map(([name, url]) => <li key={name}><strong>{name}</strong> <code>{url}</code></li>)}</ul>
        </details> : null}
        {stash.length ? <details><summary>Stash · {stash.length}</summary>
          <ul>{stash.map((entry, index) => <li key={index}><code>{`stash@{${index}}`}</code> {entry.message || 'Saved changes'}</li>)}</ul>
        </details> : null}
        {config.length ? <details><summary>Configuration · {config.length}</summary>
          <ul>{config.map(([name, value]) => <li key={name}><code>{name}</code>: {typeof value === 'string' ? value : JSON.stringify(value)}</li>)}</ul>
        </details> : null}
      </div>
      <p className="repository-state-map__history">↓ <span>{initialized ? 'Committed history' : 'History begins after initialization'}</span></p>
    </section>
  )
}
