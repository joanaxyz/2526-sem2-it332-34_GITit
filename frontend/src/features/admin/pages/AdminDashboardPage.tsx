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

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-bold text-foreground">Recent shop purchases</h2>
          <ul className="mt-3 divide-y divide-border/60">
            {data.recent_purchases.map((purchase, index) => (
              <li key={`${purchase.user_id}-${purchase.created_at}-${index}`} className="flex items-center justify-between gap-3 py-2 text-sm">
                <span className="font-medium text-foreground">{purchase.username}</span>
                <span className="text-right text-muted-foreground">
                  {formatCoins(Math.abs(purchase.amount))} GC · {formatDate(purchase.created_at)}
                </span>
              </li>
            ))}
            {data.recent_purchases.length === 0 ? (
              <li className="py-2 text-sm text-muted-foreground">No purchases yet.</li>
            ) : null}
          </ul>
        </section>

        <section className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-sm font-bold text-foreground">Recent admin actions</h2>
          <ul className="mt-3 divide-y divide-border/60">
            {data.recent_admin_actions.map((action) => (
              <li key={action.id} className="py-2 text-sm">
                <p className="font-medium text-foreground">{action.action}</p>
                <p className="text-xs text-muted-foreground">
                  {action.actor ?? 'Former admin'} · {action.target_label || 'system'} · {formatDate(action.created_at)}
                </p>
              </li>
            ))}
            {data.recent_admin_actions.length === 0 ? (
              <li className="py-2 text-sm text-muted-foreground">No admin actions yet.</li>
            ) : null}
          </ul>
        </section>
      </div>
    </div>
  )
}
