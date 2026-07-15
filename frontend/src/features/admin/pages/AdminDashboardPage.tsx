import { useQuery } from '@tanstack/react-query'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading, StatTile } from '@/features/admin/components/adminUi'
import { formatCoins, formatDate } from '@/features/admin/utils/format'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminDashboardPage() {
  const { data, isPending, isError } = useQuery({
    queryKey: queryKeys.adminOverview,
    queryFn: adminApi.overview,
  })

  if (isPending) return <LoadingState label="Loading dashboard" variant="page" />
  if (isError || !data) return <ErrorState title="Could not load dashboard" description="Try again shortly." />

  return (
    <div>
      <PageHeading title="Dashboard" description="A snapshot of the realm: players and the coin economy." />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <StatTile label="Players" value={data.users.total} hint={`+${data.users.new_7d} this week`} />
        <StatTile label="New (30d)" value={data.users.new_30d} />
        <StatTile label="Coins in circulation" value={formatCoins(data.economy.coins_in_circulation)} />
        <StatTile label="Coins spent" value={formatCoins(data.economy.coins_spent)} hint="in the shop" />
      </div>

      <section className="mt-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-bold text-foreground">Recent signups</h2>
        <ul className="mt-3 divide-y divide-border/60">
          {data.recent_signups.map((u) => (
            <li key={u.id} className="flex items-center justify-between py-2 text-sm">
              <span className="font-medium text-foreground">{u.username}</span>
              <span className="text-muted-foreground">{formatDate(u.date_joined)}</span>
            </li>
          ))}
          {data.recent_signups.length === 0 ? (
            <li className="py-2 text-sm text-muted-foreground">No signups yet.</li>
          ) : null}
        </ul>
      </section>
    </div>
  )
}
