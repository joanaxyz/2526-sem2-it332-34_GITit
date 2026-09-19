import { Link, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { drillsApi } from '@/features/drills/api/drillsApi'
import { DrillSession } from '@/features/drills/components/DrillSession'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { drillExitPath } from '@/features/drills/utils/drillRoutes'
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
  const plan = useQuery({
    queryKey: queryKeys.levelDrill(id),
    queryFn: () => drillsApi.getPlan(id),
    enabled: Number.isFinite(id),
    // Content is derived from seed data, so it is stable for a session;
    // progress is refetched by the map, not by re-entering the drill.
    staleTime: 5 * 60 * 1000,
  })

  if (plan.isPending) {
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
