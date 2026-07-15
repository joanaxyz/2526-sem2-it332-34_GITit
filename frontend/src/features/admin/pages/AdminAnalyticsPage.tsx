import { useQuery } from '@tanstack/react-query'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading, StatTile } from '@/features/admin/components/adminUi'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminAnalyticsPage() {
  const { data, isPending, isError } = useQuery({ queryKey: queryKeys.adminAnalytics, queryFn: adminApi.analytics })

  if (isPending) return <LoadingState label="Loading analytics" variant="page" />
  if (isError || !data) return <ErrorState title="Could not load analytics" description="Try again shortly." />

  const passRate = data.runs.total > 0 ? Math.round((data.runs.passed / data.runs.total) * 100) : 0
  return (
    <div>
      <PageHeading title="Progress & Analytics" description="How learners are moving through the curriculum." />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Adventure runs" value={data.runs.total} />
        <StatTile label="Pass rate" value={`${passRate}%`} hint={`${data.runs.passed} passed`} />
        <StatTile label="Active learners" value={data.active_learners_30d} hint="last 30 days" />
        <StatTile label="Level completions" value={data.completions.total} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-bold text-foreground">Runs by status</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {Object.entries(data.runs.by_status).map(([status, count]) => (
              <li key={status} className="flex items-center justify-between rounded-md bg-background/40 px-3 py-1.5">
                <span className="capitalize text-muted-foreground">{status}</span>
                <span className="font-bold text-foreground">{count}</span>
              </li>
            ))}
            {Object.keys(data.runs.by_status).length === 0 ? (
              <li className="text-muted-foreground">No runs yet.</li>
            ) : null}
          </ul>
        </section>

        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-bold text-foreground">Completions</h2>
          <ul className="mt-3 space-y-2 text-sm">
            <li className="flex items-center justify-between rounded-md bg-background/40 px-3 py-1.5">
              <span className="text-muted-foreground">Adventure levels</span>
              <span className="font-bold text-foreground">{data.completions.adventure}</span>
            </li>
            <li className="flex items-center justify-between rounded-md bg-background/40 px-3 py-1.5">
              <span className="text-muted-foreground">Challenge levels</span>
              <span className="font-bold text-foreground">{data.completions.challenge}</span>
            </li>
          </ul>
        </section>
      </div>

      <section className="mt-6 overflow-hidden rounded-lg border border-border bg-card">
        <div className="border-b border-border px-5 py-3 text-sm font-bold text-foreground">Per story</div>
        <table className="w-full text-sm">
          <thead className="border-b border-border text-left text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-5 py-2 font-semibold">Story</th>
              <th className="px-5 py-2 font-semibold">Runs</th>
              <th className="px-5 py-2 font-semibold">Passed</th>
            </tr>
          </thead>
          <tbody>
            {data.per_story.map((story) => (
              <tr key={story.slug} className="border-b border-border/40">
                <td className="px-5 py-2.5 font-medium text-foreground">{story.title}</td>
                <td className="px-5 py-2.5 text-muted-foreground">{story.runs}</td>
                <td className="px-5 py-2.5 text-muted-foreground">{story.passed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
