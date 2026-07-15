import { Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'

import { authApi } from '@/shared/auth/authApi'
import { useAuthStore } from '@/shared/auth/useAuth'
import { queryKeys } from '@/shared/api/queryKeys'
import { LoadingState } from '@/shared/components/LoadingState'

export function Protected({ children }: { children: ReactElement }) {
  const token = useAuthStore((state) => state.accessToken)
  const user = useAuthStore((state) => state.user)
  const bootstrapQuery = useQuery({
    queryKey: queryKeys.authBootstrap,
    queryFn: async () => {
      if (token) {
        const user = await authApi.me()
        useAuthStore.getState().setSession(token, user)
        return user
      }
      const refreshed = await authApi.refresh()
      useAuthStore.getState().setAccessToken(refreshed.access)
      const user = await authApi.me()
      useAuthStore.getState().setSession(refreshed.access, user)
      return user
    },
    enabled: !token || !user,
    retry: false,
  })

  if ((!token || !user) && bootstrapQuery.isPending) {
    return (
      <LoadingState
        description="Checking your saved login before opening the workspace."
        label="Restoring session"
        variant="screen"
      />
    )
  }
  if (!token || (!user && bootstrapQuery.isError)) return <Navigate replace to="/login" />
  return children
}
