import { Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'
import { useQuery } from '@tanstack/react-query'

import { authApi } from '@/shared/auth/authApi'
import {
  beginAuthConfirmation,
  confirmAuthSession,
  useAuthStore,
} from '@/shared/auth/useAuth'
import { refreshSharedAccessToken } from '@/shared/api/httpClient'
import { queryKeys } from '@/shared/api/queryKeys'
import { LoadingScreen } from '@/shared/components/LoadingScreen'

export function Protected({ children }: { children: ReactElement }) {
  const token = useAuthStore((state) => state.accessToken)
  const user = useAuthStore((state) => state.user)
  const bootstrapQuery = useQuery({
    queryKey: queryKeys.authBootstrap,
    queryFn: async () => {
      if (token) {
        const user = await authApi.me()
        confirmAuthSession(token, user)
        return user
      }
      // Shares the tab's single-flight refresh. Calling /auth/refresh/ directly
      // here raced the 401 retry path, and single-use rotation turned the loser
      // into a spurious logout.
      const access = await refreshSharedAccessToken()
      beginAuthConfirmation(access)
      const user = await authApi.me()
      confirmAuthSession(access, user)
      return user
    },
    enabled: !token || !user,
    // A cached bootstrap must never satisfy a later re-entry: the store drops
    // the token or the user on purpose (cross-tab rotation, confirmation
    // hand-off) and each of those has to be re-confirmed, not assumed.
    staleTime: 0,
    retry: false,
  })

  // An incomplete session is a session being restored, not a missing one. Only
  // a bootstrap that actually failed sends the player back to the front door.
  if (!token || !user) {
    if (bootstrapQuery.isError) return <Navigate replace to="/login" />
    return (
      <LoadingScreen
        description="Checking your saved login before opening the workspace."
        label="Restoring session"
      />
    )
  }

  return children
}
