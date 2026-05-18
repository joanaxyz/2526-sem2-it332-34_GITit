import { Navigate } from 'react-router-dom'
import type { ReactElement } from 'react'

import { useAuthStore } from '@/features/auth/hooks/useAuth'

export function Protected({ children }: { children: ReactElement }) {
  const token = useAuthStore((state) => state.accessToken)
  if (!token) return <Navigate replace to="/login" />
  return children
}
