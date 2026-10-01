import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'

import { drillsApi } from '@/features/drills/api/drillsApi'
import { DrillSession } from '@/features/drills/components/DrillSession'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { drillExitPath } from '@/features/drills/utils/drillRoutes'
import { waitForDrillWrites } from '@/features/drills/utils/drillRunCache'
import { queryKeys } from '@/shared/api/queryKeys'
import { storyPath } from '@/shared/navigation/routes'

/**
 * Squire's Drill for one adventure level.
 *
 * The rung between reading a chapter and typing at a live prompt: short
 * recall practice on exactly the commands this level will ask for. It is
 * always optional and never gates the level.
 */
export function DrillPage() {
  const { levelId } = useParams<{ levelId: string }>()
  const id = Number(levelId)

  return <DrillEntry key={id} id={id} />
}

function DrillEntry({ id }: { id: number }) {
  const queryClient = useQueryClient()
  const [entered, setEntered] = useState(false)
  const plan = useQuery({
    queryKey: queryKeys.levelDrill(id),
    queryFn: async ({ signal }) => {
      await waitForDrillWrites(queryClient, id, signal)
      signal.throwIfAborted()
      return drillsApi.getPlan(id)
    },
    enabled: Number.isFinite(id),
    // The payload includes this player's live resume state as well as content.
    // Read it on every entry, after any writes from the previous visit settle.
    staleTime: 0,
    refetchOnMount: 'always',
  })

  useEffect(() => {
    // A pending mutation can update the cache before the entry GET finishes.
    // Once entered, background refreshes must not remount the active session.
    if (plan.isFetchedAfterMount && !plan.isFetching) setEntered(true)
  }, [plan.isFetchedAfterMount, plan.isFetching])

  if (plan.isPending || !entered) {
    return (
      <LoadingScreen
        label="Opening the drill"
        description="Gathering the commands this level will ask for."
      />
    )
  }

  if (plan.isError || !plan.data) {
    return (
      <div className="drill-screen drill-screen--message">
        <ErrorState
          title="Could not open this drill"
          description={
            plan.error instanceof Error
              ? plan.error.message
              : 'This level is not available to drill yet.'
          }
        />
        <Link className="ui-button ui-button--outline" to={storyPath()}>
          Back to the level map
        </Link>
      </div>
    )
  }

  if (!plan.data.available) {
    return (
      <div className="drill-screen drill-screen--message">
        <section className="drill-empty">
          <p className="drill-summary-eyebrow">No drill here</p>
          <h2>{plan.data.level.title}</h2>
          <p>
            This level does not teach a named command form yet, so there is nothing to rehearse.
            Play it directly instead.
          </p>
        </section>
        <Link className="ui-button ui-button--default" to={drillExitPath(plan.data)}>
          Back to the level map
        </Link>
      </div>
    )
  }

  return <DrillSession plan={plan.data} />
}
