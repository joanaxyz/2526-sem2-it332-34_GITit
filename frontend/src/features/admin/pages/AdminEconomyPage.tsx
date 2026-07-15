import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminEconomyPage() {
  const queryClient = useQueryClient()
  const [userId, setUserId] = useState('')
  const [amount, setAmount] = useState('')
  const [reason, setReason] = useState('')

  const txQuery = useQuery({
    queryKey: queryKeys.adminTransactions(),
    queryFn: () => adminApi.transactions(),
  })

  const adjust = useMutation({
    mutationFn: adminApi.adjustCoins,
    onSuccess: () => {
      setAmount('')
      setReason('')
      queryClient.invalidateQueries({ queryKey: queryKeys.adminTransactions() })
      queryClient.invalidateQueries({ queryKey: queryKeys.adminOverview })
    },
  })

  return (
    <div>
      <PageHeading title="Economy" description="The GitCoin ledger, plus manual grants and deductions." />

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-bold text-foreground">Manual adjustment</h2>
        <p className="mt-1 text-xs text-muted-foreground">Positive grants coins; negative deducts them.</p>
        <form
          className="mt-3 flex flex-wrap gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            const uid = Number(userId)
            const amt = Number(amount)
            if (!Number.isFinite(uid) || !Number.isFinite(amt) || amt === 0) return
            adjust.mutate({ user_id: uid, amount: amt, reason: reason.trim() || 'admin_adjust' })
          }}
        >
          <input
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="User ID"
            inputMode="numeric"
            className="h-9 w-28 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50"
          />
          <input
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount (±)"
            inputMode="numeric"
            className="h-9 w-32 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50"
          />
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Reason (optional)"
            className="h-9 flex-1 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50"
          />
          <Button type="submit" size="sm" disabled={adjust.isPending}>Apply</Button>
        </form>
        {adjust.isError ? (
          <p className="mt-2 text-xs text-destructive">Adjustment failed (insufficient balance or invalid input).</p>
        ) : null}
      </section>

      <section className="overflow-hidden rounded-lg border border-border bg-card">
        <div className="border-b border-border px-5 py-3 text-sm font-bold text-foreground">Recent transactions</div>
        {txQuery.isPending ? (
          <LoadingState label="Loading ledger" variant="panel" />
        ) : txQuery.isError || !txQuery.data ? (
          <ErrorState title="Could not load ledger" description="Try again shortly." />
        ) : (
          <table className="w-full text-sm">
            <thead className="border-b border-border text-left text-xs uppercase text-muted-foreground">
              <tr>
                <th className="px-5 py-2 font-semibold">User</th>
                <th className="px-5 py-2 font-semibold">Amount</th>
                <th className="px-5 py-2 font-semibold">Reason</th>
                <th className="px-5 py-2 font-semibold">When</th>
              </tr>
            </thead>
            <tbody>
              {txQuery.data.results.map((tx) => (
                <tr key={tx.id} className="border-b border-border/40">
                  <td className="px-5 py-2 text-foreground">{tx.username}</td>
                  <td className={'px-5 py-2 font-bold ' + (tx.amount < 0 ? 'text-destructive' : 'text-primary')}>
                    {tx.amount > 0 ? '+' : ''}
                    {tx.amount}
                  </td>
                  <td className="px-5 py-2 text-muted-foreground">{tx.reason}</td>
                  <td className="px-5 py-2 text-muted-foreground">{new Date(tx.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {txQuery.data.results.length === 0 ? (
                <tr><td colSpan={4} className="px-5 py-6 text-center text-muted-foreground">No transactions yet.</td></tr>
              ) : null}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
