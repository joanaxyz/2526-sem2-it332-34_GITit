import { Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'

import { authApi } from '@/features/auth/api/authApi'
import { useAuthStore } from '@/features/auth/hooks/useAuth'
import { queryKeys } from '@/shared/api/queryKeys'
import { LoadingState } from '@/shared/components/LoadingState'

export function Protected({ children }: { children: ReactElement }) {
  const token = useAuthStore((state) => state.accessToken)
  const bootstrapQuery = useQuery({
    queryKey: queryKeys.authBootstrap,
    queryFn: async () => {
      const refreshed = await authApi.refresh()
      useAuthStore.getState().setAccessToken(refreshed.access)
      const user = await authApi.me()
      useAuthStore.getState().setSession(refreshed.access, user)
      return user
    },
    enabled: !token,
    retry: false,
  })

  if (!token && bootstrapQuery.isPending) return <LoadingState label="Restoring session" />
  if (!token) return <Navigate replace to="/login" />
  return children
}
