import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'

import { subscribeToChallengeRunSync } from '@/features/challenges/utils/challengeRunCache'
import { ApiError } from '@/shared/api/apiError'

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: (failureCount, error) => {
              if (error instanceof ApiError && error.status < 500) return false
              return failureCount < 1
            },
            refetchOnWindowFocus: false,
          },
        },
      }),
  )

  useEffect(() => subscribeToChallengeRunSync(queryClient), [queryClient])

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
