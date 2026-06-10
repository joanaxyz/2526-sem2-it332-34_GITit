import { useEffect } from 'react'
import { useParams } from 'react-router-dom'

import { AdventureSession } from '@/features/command-adventures/components/AdventureSession'
import { useStartAdventureRun } from '@/features/command-adventures/hooks/useAdventureRun'
import { LoadingState } from '@/shared/components/LoadingState'

export function CommandAdventurePage() {
  const { adventureSlug } = useParams<{ adventureSlug: string }>()
  const start = useStartAdventureRun()

  useEffect(() => {
    if (adventureSlug && start.isIdle) {
      start.mutate(adventureSlug)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [adventureSlug])

  if (!adventureSlug) return <p className="p-8 text-sm text-red-400">Missing adventure.</p>
  if (start.isPending || start.isIdle)
    return (
      <LoadingState
        description="Preparing the repository, terminal, and command challenge."
        label="Starting adventure"
        variant="screen"
      />
    )
  if (start.isError || !start.data)
    return <p className="p-8 text-sm text-red-400">Could not start this adventure.</p>

  return (
    <AdventureSession
      runId={start.data.id}
      onRestart={() => adventureSlug && start.mutate(adventureSlug)}
    />
  )
}
