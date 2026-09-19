import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'

import { queryKeys } from '@/shared/api/queryKeys'
import { useAuthStore } from '@/shared/auth/useAuth'
import { LoadingScreen } from '@/shared/components/LoadingScreen'
import { LoadingState } from '@/shared/components/LoadingState'
import { cn } from '@/shared/utils/cn'

const KINDS = ['screen', 'panel', 'inline', 'compact'] as const
const COMPANIONS = ['unknown', 'none', 'blue', 'white', 'black'] as const
const NAMES = ['anonymous', 'Joana', 'bartholomew_the_longwinded'] as const

function pick<T extends readonly string[]>(options: T, value: string | null, fallback: T[number]): T[number] {
  return options.includes(value as T[number]) ? (value as T[number]) : fallback
}

function LoadingPreviewPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const kind = pick(KINDS, searchParams.get('variant'), 'screen')
  const companion = pick(COMPANIONS, searchParams.get('companion'), 'blue')
  const playerName = pick(NAMES, searchParams.get('name'), 'anonymous')

  // The loader reads the equipped companion straight from the catalog cache,
  // so the preview drives it by writing that cache rather than by props.
  useEffect(() => {
    if (companion === 'unknown') {
      queryClient.removeQueries({ queryKey: queryKeys.shopCatalog })
      return
    }
    queryClient.setQueryData(queryKeys.shopCatalog, {
      active_companion: companion === 'none' ? null : companion,
      items: [],
      owned_item_ids: [],
    })
  }, [companion, queryClient])

  // The first-run greeting names the player, so the harness has to be one.
  useEffect(() => {
    useAuthStore.setState({ user: playerName === 'anonymous' ? null : ({ username: playerName } as never) })
  }, [playerName])

  const set = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    next.set(key, value)
    setSearchParams(next, { replace: true })
  }

  const group = <T extends readonly string[]>(options: T, active: string, key: string) =>
    options.map((option) => (
      <button
        className={cn('ui-button ui-button--sm', active === option ? 'ui-button--default' : 'ui-button--outline')}
        key={option}
        onClick={() => set(key, option)}
        type="button"
      >
        {option}
      </button>
    ))

  return (
    <div className="min-h-screen bg-background">
      <div
        className="flex flex-wrap items-center gap-2 border-b p-3"
        style={{ borderColor: 'var(--border-subtle)' }}
      >
        {group(KINDS, kind, 'variant')}
        <span className="h-5 w-px" style={{ background: 'var(--border-subtle)' }} />
        {group(COMPANIONS, companion, 'companion')}
        <span className="h-5 w-px" style={{ background: 'var(--border-subtle)' }} />
        {group(NAMES, playerName, 'name')}
      </div>

      {kind === 'screen' ? (
        // The screen covers this harness too - that is the point of it.
        <LoadingScreen
          description="Preparing the repository, terminal, and adventure workspace."
          key={`${companion}-${playerName}`}
          label="Starting adventure"
        />
      ) : (
        <LoadingState
          description="Preparing the repository, terminal, and adventure workspace."
          key={kind}
          label="Starting adventure"
          variant={kind}
        />
      )}
    </div>
  )
}

/**
 * Dev-only harness for both loaders: loading states are transient by nature, so
 * this is the only way to look at one long enough to judge it. `screen` is the
 * full-page companion overlay; every other option is the in-place spinner.
 * Compiled away in production with the rest of `/dev`.
 */
export const Component = LoadingPreviewPage
