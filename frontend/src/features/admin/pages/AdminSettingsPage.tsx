import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { adminApi } from '@/features/admin/api/adminApi'
import { PageHeading } from '@/features/admin/components/adminUi'
import { adminErrorMessage } from '@/features/admin/utils/errors'
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

  if (isPending) return <LoadingState label="Loading settings" variant="page" />
  if (isError || !data) return <ErrorState title="Could not load settings" description="Try again shortly." />

  return (
    <div>
      <PageHeading title="Settings" description="Runtime controls supported by this deployment." />

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
            <p className="text-xs text-muted-foreground">No supported feature flags.</p>
          ) : null}
        </div>
        {saveFlag.isError ? (
          <p role="alert" className="mt-3 text-xs text-destructive">
            {adminErrorMessage(saveFlag.error, 'The feature flag could not be saved.')}
          </p>
        ) : null}
      </section>

    </div>
  )
}
