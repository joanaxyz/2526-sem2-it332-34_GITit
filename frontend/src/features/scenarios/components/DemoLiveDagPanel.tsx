import type { RepositorySnapshot } from '@/features/practice/types'
import { LiveDagPanel } from '@/features/practice/components/LiveDagPanel'

export function DemoLiveDagPanel({ snapshot }: { snapshot: RepositorySnapshot }) {
  return (
    <LiveDagPanel
      title="Demo Live DAG"
      snapshot={snapshot}
      className="h-full min-h-[18rem]"
      contentClassName="h-[18rem]"
    />
  )
}
