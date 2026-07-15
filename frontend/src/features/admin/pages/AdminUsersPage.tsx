import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type ReactNode } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { formatCoins, formatDate } from '@/features/admin/utils/format'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminUsersPage() {
  const queryClient = useQueryClient()
  const [query, setQuery] = useState('')
  const [search, setSearch] = useState('')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const usersQuery = useQuery({
    queryKey: queryKeys.adminUsers(search),
    queryFn: () => adminApi.users(search),
  })

  return (
    <div>
      <PageHeading title="Users" description="Search players, inspect their wallet and plan, and run staff actions." />

      <form
        className="mb-4 flex gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          setSearch(query.trim())
        }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search username or email…"
          className="h-9 flex-1 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50"
        />
        <Button type="submit" variant="outline" size="sm">Search</Button>
      </form>

      <div className="grid gap-5 lg:grid-cols-[1fr_360px]">
        <div className="overflow-hidden rounded-lg border border-border bg-card">
          {usersQuery.isPending ? (
            <LoadingState label="Loading users" variant="panel" />
          ) : usersQuery.isError ? (
            <ErrorState title="Could not load users" description="Try again shortly." />
          ) : (
            <table className="w-full text-sm">
              <thead className="border-b border-border text-left text-xs uppercase text-muted-foreground">
                <tr>
                  <th className="px-4 py-2 font-semibold">User</th>
                  <th className="px-4 py-2 font-semibold">Joined</th>
                </tr>
              </thead>
              <tbody>
                {usersQuery.data.results.map((u) => (
                  <tr
                    key={u.id}
                    onClick={() => setSelectedId(u.id)}
                    className={
                      'cursor-pointer border-b border-border/40 transition hover:bg-secondary/40 ' +
                      (selectedId === u.id ? 'bg-secondary/50' : '')
                    }
                  >
                    <td className="px-4 py-2.5">
                      <div className="font-medium text-foreground">
                        {u.username}
                        {u.is_staff ? <span className="ml-2 text-xs text-primary">staff</span> : null}
                        {!u.is_active ? <span className="ml-2 text-xs text-destructive">disabled</span> : null}
                      </div>
                      <div className="text-xs text-muted-foreground">{u.email}</div>
                    </td>
                    <td className="px-4 py-2.5 text-muted-foreground">{formatDate(u.date_joined)}</td>
                  </tr>
                ))}
                {usersQuery.data.results.length === 0 ? (
                  <tr><td colSpan={2} className="px-4 py-6 text-center text-muted-foreground">No users found.</td></tr>
                ) : null}
              </tbody>
            </table>
          )}
        </div>

        <UserDetailPanel
          userId={selectedId}
          onChanged={() => {
            queryClient.invalidateQueries({ queryKey: queryKeys.adminUsers(search) })
          }}
        />
      </div>
    </div>
  )
}

function UserDetailPanel({ userId, onChanged }: { userId: number | null; onChanged: () => void }) {
  const queryClient = useQueryClient()
  const [coinAmount, setCoinAmount] = useState('')

  const detailQuery = useQuery({
    queryKey: queryKeys.adminUser(userId ?? 0),
    queryFn: () => adminApi.user(userId as number),
    enabled: userId != null,
  })

  const action = useMutation({
    mutationFn: (payload: Parameters<typeof adminApi.userAction>[1]) =>
      adminApi.userAction(userId as number, payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(queryKeys.adminUser(userId ?? 0), updated)
      onChanged()
    },
  })

  if (userId == null) {
    return (
      <div className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        Select a user to manage their plan, coins, and access.
      </div>
    )
  }
  if (detailQuery.isPending) return <LoadingState label="Loading user" variant="panel" />
  if (detailQuery.isError || !detailQuery.data)
    return <ErrorState title="Could not load user" description="Try again shortly." />

  const user = detailQuery.data
  return (
    <div className="h-fit rounded-lg border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-lg font-black text-foreground">{user.username}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <Stat label="Wallet" value={`${formatCoins(user.wallet.balance)} GC`} />
        <Stat label="Entitlements" value={user.entitlement_count} />
        <Stat label="Joined" value={formatDate(user.date_joined)} />
      </dl>

      <div className="mt-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Adjust coins</p>
        <div className="flex gap-2">
          <input
            value={coinAmount}
            onChange={(e) => setCoinAmount(e.target.value)}
            placeholder="e.g. 500 or -100"
            inputMode="numeric"
            className="h-8 w-full rounded-md border border-border bg-background/40 px-2 text-sm outline-none focus:border-primary/50"
          />
          <Button
            size="sm"
            variant="outline"
            disabled={action.isPending || !coinAmount.trim()}
            onClick={() => {
              const amount = Number(coinAmount)
              if (!Number.isFinite(amount) || amount === 0) return
              action.mutate({ action: 'grant_coins', amount, reason: 'admin_grant' })
              setCoinAmount('')
            }}
          >
            Apply
          </Button>
        </div>
      </div>

      <div className="mt-4 flex gap-2 border-t border-border/60 pt-4">
        <Button
          size="sm"
          variant="outline"
          disabled={action.isPending}
          onClick={() => action.mutate({ action: 'set_staff', value: !user.is_staff })}
          className="flex-1"
        >
          {user.is_staff ? 'Revoke staff' : 'Make staff'}
        </Button>
        <Button
          size="sm"
          variant={user.is_active ? 'destructive' : 'outline'}
          disabled={action.isPending}
          onClick={() => action.mutate({ action: 'set_active', value: !user.is_active })}
          className="flex-1"
        >
          {user.is_active ? 'Disable' : 'Enable'}
        </Button>
      </div>
      {action.isError ? (
        <p className="mt-3 text-xs text-destructive">Action failed. Check the amount and try again.</p>
      ) : null}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-md bg-background/40 px-3 py-2">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="font-semibold text-foreground">{value}</dd>
    </div>
  )
}
