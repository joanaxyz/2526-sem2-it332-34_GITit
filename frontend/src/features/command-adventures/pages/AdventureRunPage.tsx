import { useParams } from 'react-router-dom'

import { AdventureSession } from '@/features/command-adventures/components/AdventureSession'

export function AdventureRunPage() {
  const { runId } = useParams<{ runId: string }>()
  const parsedRunId = runId ? Number(runId) : NaN

  if (!Number.isFinite(parsedRunId)) {
    return <p className="p-8 text-sm text-red-400">Missing adventure run.</p>
  }

  return <AdventureSession runId={parsedRunId} />
}
