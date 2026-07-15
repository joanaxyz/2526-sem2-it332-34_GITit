import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { Button } from '@/shared/components/Button'
import { ErrorState } from '@/shared/components/ErrorState'
import { LoadingState } from '@/shared/components/LoadingState'
import { queryKeys } from '@/shared/api/queryKeys'

export function AdminSettingsPage() {
  const queryClient = useQueryClient()
  const { data, isPending, isError } = useQuery({ queryKey: queryKeys.adminSettings, queryFn: adminApi.settings })

  const saveFlag = useMutation({
    mutationFn: adminApi.saveFlag,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.adminSettings }),
  })

  const [newKey, setNewKey] = useState('')
  const [newLabel, setNewLabel] = useState('')

  if (isPending) return <LoadingState label="Loading settings" variant="page" />
  if (isError || !data) return <ErrorState title="Could not load settings" description="Try again shortly." />

  return (
    <div>
      <PageHeading title="Settings" description="Feature flags and the asset tag vocabulary." />

      <section className="mb-6 rounded-lg border border-border bg-card p-5">
        <h2 className="text-sm font-bold text-foreground">Feature flags</h2>
        <div className="mt-3 grid gap-2">
          {data.feature_flags.map((flag) => (
            <div key={flag.key} className="flex items-center justify-between rounded-md bg-background/40 px-3 py-2">
              <div>
                <p className="text-sm font-medium text-foreground">{flag.label}</p>
                <p className="text-xs text-muted-foreground">{flag.key}{flag.description ? ` · ${flag.description}` : ''}</p>
              </div>
              <Button
                size="sm"
                variant={flag.enabled ? 'default' : 'outline'}
                disabled={saveFlag.isPending}
                onClick={() => saveFlag.mutate({ key: flag.key, enabled: !flag.enabled })}
              >
                {flag.enabled ? 'On' : 'Off'}
              </Button>
            </div>
          ))}
          {data.feature_flags.length === 0 ? (
            <p className="text-xs text-muted-foreground">No feature flags yet.</p>
          ) : null}
        </div>

        <form
          className="mt-4 flex flex-wrap gap-2 border-t border-border/60 pt-4"
          onSubmit={(e) => {
            e.preventDefault()
            if (newKey.trim()) {
              saveFlag.mutate({ key: newKey.trim(), label: newLabel.trim() || newKey.trim(), enabled: false })
              setNewKey('')
              setNewLabel('')
            }
          }}
        >
          <input value={newKey} onChange={(e) => setNewKey(e.target.value)} placeholder="flag-key" className="h-9 w-44 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50" />
          <input value={newLabel} onChange={(e) => setNewLabel(e.target.value)} placeholder="Label" className="h-9 flex-1 rounded-md border border-border bg-background/40 px-3 text-sm outline-none focus:border-primary/50" />
          <Button type="submit" size="sm" variant="outline" disabled={saveFlag.isPending}>Add flag</Button>
        </form>
      </section>

    </div>
  )
}
